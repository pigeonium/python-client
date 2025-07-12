import requests
import pigeonium
from typing import Optional, Dict, Any

class PigeoniumClient:
    """
    Pigeoniumネットワークと対話するためのクライアント。
    APIサーバーを介して、残高照会、トランザクション送信、コントラクトデプロイなどの機能を提供します。
    """

    def __init__(self, base_url: str = "http://127.0.0.1:14540"):
        """
        PigeoniumClientを初期化します。
        初期化時にサーバーに接続し、ネットワーク情報を取得・設定します。

        Args:
            base_url (str): Pigeonium APIサーバーのベースURL。
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.network_info: Optional[Dict[str, str|int|Dict]] = None

        self._fetch_and_apply_network_info()

    def _fetch_and_apply_network_info(self) -> None:
        """サーバーからネットワーク情報を取得し、ローカルのpigeonium.Configを更新します。"""
        response = self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        self.network_info = response.json()

        pigeonium.Config.NetworkName = self.network_info['networkName']
        pigeonium.Config.NetworkId = self.network_info['networkId']
        pigeonium.Config.ContractDeployCost = self.network_info['contractDeployCost']
        pigeonium.Config.AdminPublicKey = bytes.fromhex(self.network_info['adminPublicKey'])

        base_currency_info = self.network_info['baseCurrency']
        base_currency = pigeonium.Currency()
        base_currency.currencyId = bytes.fromhex(base_currency_info['currencyId'])
        base_currency.name = base_currency_info['name']
        base_currency.symbol = base_currency_info['symbol']
        base_currency.issuer = bytes.fromhex(base_currency_info['issuer'])
        base_currency.supply = base_currency_info['supply']
        pigeonium.Config.BaseCurrency = base_currency

        print(f"ネットワーク '{self.network_info['networkName']}' (ID: {self.network_info['networkId']}) に接続しました。")

    def _post(self, endpoint: str, json_data: Dict[str, str|int]) -> Dict[str, str|int]:
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=json_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"{e.response.status_code}: {e.response.text}")
            raise e

    def _get(self, endpoint: str, params: dict={}) -> Dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"{e.response.status_code}: {e.response.text}")
            raise e

    @staticmethod
    def generate_wallet() -> pigeonium.Wallet:
        """
        新しいPigeoniumウォレットを生成します。
        """
        return pigeonium.Wallet.generate()

    @staticmethod
    def wallet_from_private_key(private_key_hex: str) -> pigeonium.Wallet:
        """
        16進数文字列の秘密鍵からウォレットを復元します。
        """
        return pigeonium.Wallet.fromPrivate(bytes.fromhex(private_key_hex))

    def get_balance(self, address: bytes, currency_id: bytes) -> int:
        """
        指定されたアドレスの単一の通貨残高を取得します。
        """
        result = self._get(f"/balance/{address.hex()}/{currency_id.hex()}")
        return result.get('amount', 0)
    
    def get_balances(self, address: bytes) -> Dict[bytes, int]:
        """
        指定されたアドレスの通貨残高を取得します。
        """
        result = self._get(f"/balances/{address.hex()}")
        bals = {}
        for cu_id in result.keys():
            bals[bytes.fromhex(cu_id)] = result[cu_id]
        return bals
    
    def get_currency(
        self,
        currency_id: Optional[bytes] = None,
        name: Optional[str] = None,
        symbol: Optional[str] = None,
        issuer: Optional[bytes] = None
    ) -> pigeonium.Currency|None:
        try:
            if currency_id:
                response = self._get(f"/currency", {"currencyId": currency_id.hex()})
            elif name:
                response = self._get(f"/currency", {"name": name})
            elif symbol:
                response = self._get(f"/currency", {"symbol": symbol})
            elif issuer:
                response = self._get(f"/currency", {"issuer": issuer.hex()})
            cu = pigeonium.Currency()
            cu.currencyId = bytes.fromhex(response['currencyId'])
            cu.name = response['name']
            cu.symbol = response['symbol']
            cu.issuer = bytes.fromhex(response['issuer'])
            cu.supply = response['supply']
            return cu
        except:
            return None
    
    def send_transaction(
        self,
        source_wallet: pigeonium.Wallet,
        dest_address: bytes,
        currency_id: bytes,
        amount: int,
        fee_amount: int = 0,
        input_data: bytes = b''
    ) -> pigeonium.Transaction:
        """
        通貨を送信するトランザクションを作成し、ネットワークにブロードキャストします。

        Args:
            source_wallet (pigeonium.Wallet): 送信元ウォレット。
            dest_address_hex (str): 宛先アドレスの16進数文字列。
            currency_id_hex (str): 送信する通貨のID(16進数文字列)。
            amount (int): 送信量 (最小単位)。
            fee_amount (int, optional): 手数料。 Defaults to 0.
            input_data (bytes, optional): トランザクションに含める追加データ。 Defaults to b''.

        Returns:
            pigeonium.Transaction: サーバーから返された実行後のトランザクション情報。
        """
        tx = pigeonium.Transaction.create(
            source=source_wallet,
            dest=bytes.fromhex(dest_address.hex()),
            currencyId=bytes.fromhex(currency_id.hex()),
            amount=amount,
            feeAmount=fee_amount,
            inputData=input_data
        )

        payload = {
            "source": source_wallet.address.hex(),
            "dest": dest_address.hex(),
            "currencyId": currency_id.hex(),
            "amount": amount,
            "feeAmount": fee_amount,
            "inputData": input_data.hex(),
            "publicKey": source_wallet.publicKey.hex(),
            "signature": tx.signature.hex(),
        }

        response = self._post("/transaction", payload)

        return pigeonium.Transaction.fromHexDict(response)

    def deploy_contract(
        self,
        sender_wallet: pigeonium.Wallet,
        script: str
    ) -> pigeonium.Transaction:
        """
        スマートコントラクトをネットワークにデプロイします。
        デプロイ費用は基軸通貨で支払われます。

        Args:
            sender_wallet (pigeonium.Wallet): デプロイ費用を支払うウォレット。
            script (str): スマートコントラクトのソースコード。

        Returns:
            pigeonium.Transaction: サーバーから返されたデプロイトランザクションの情報。
        """
        contract = pigeonium.Contract(script)
        base_currency_id = pigeonium.Config.BaseCurrency.currencyId

        deploy_tx = pigeonium.Transaction.create(
            source=sender_wallet,
            dest=bytes(16),
            currencyId=base_currency_id,
            amount=contract.deployCost,
            feeAmount=0,
            inputData=contract.address
        )

        script_hash = pigeonium.Utils.sha3_256(script.encode())
        script_signature = sender_wallet.sign(script_hash)

        payload = {
            "sender": sender_wallet.address.hex(),
            "script": script,
            "publicKey": sender_wallet.publicKey.hex(),
            "signature": script_signature.hex(),
            "deployTransaction": {
                "source": sender_wallet.address.hex(),
                "dest": "00" * 16,
                "currencyId": base_currency_id.hex(),
                "amount": contract.deployCost,
                "feeAmount": 0,
                "inputData": contract.address.hex(),
                "publicKey": sender_wallet.publicKey.hex(),
                "signature": deploy_tx.signature.hex(),
            }
        }

        response = self._post("/contract", payload)
        return pigeonium.Transaction.fromHexDict(response)


if __name__ == '__main__':    
    # クライアントの初期化
    API_URL = "https://pigeonium.h4ribote.net/server"
    client = PigeoniumClient(API_URL)

    base_currency_id = pigeonium.Config.BaseCurrency.currencyId

    # ウォレットの準備
    wallet1 = client.generate_wallet()
    wallet2 = client.generate_wallet()
    print("\n--- ウォレット情報 ---")
    print(f"Wallet 1 Address: {wallet1.address.hex()}")
    print(f"Wallet 2 Address: {wallet2.address.hex()}")
    print(f"Wallet 1 Secret Key: {wallet1.privateKey.hex()}")
    print(f"Wallet 2 Secret Key: {wallet2.privateKey.hex()}")
    print("-" * 20)


    # 例A: 残高の確認
    print("\n--- 残高確認 ---")
    bals = client.get_balances(wallet1.address)
    if bals:
        for bal_cu_id in bals.keys():
            cu = client.get_currency(bal_cu_id)
            print(f"{pigeonium.Utils.convertAmount(bals[bal_cu_id])} {cu.symbol} ({cu.name})")
    else:
        print("残高なし")
    print("-" * 20)


    # 例B: トランザクションの送信
    print("\n--- トランザクション送信 ---")
    response = client.send_transaction(
        source_wallet=wallet1,
        dest_address=wallet2.address,
        currency_id=base_currency_id,
        amount=10000
    )
    print("トランザクション成功:")
    print(f"{response.source.hex()} "
          f"=({pigeonium.Utils.convertAmount(response.amount)} {client.get_currency(response.currencyId).symbol})=> "
          f"{response.dest.hex()}")
    print("-" * 20)

    # 例C: スマートコントラクトのデプロイ・実行
    print("\n--- コントラクトデプロイ ---")
    sample_script = """if transaction.inputData: setVariable(inputData, b'Hello Pigeonium!')"""
    response = client.deploy_contract(
        sender_wallet=wallet1,
        script=sample_script
    )
    print("コントラクトデプロイ成功:")
    print(f"Deployed contract address: {response.inputData.hex()}")

    print("\n--- コントラクト実行 ---")
    response = client.send_transaction(
        source_wallet=wallet1,
        dest_address=response.inputData,
        currency_id=base_currency_id,
        amount=0,
        input_data=b"test")
    print("コントラクト実行成功:")
    print(f"indexId: {response.indexId}")
    print("-" * 20)
