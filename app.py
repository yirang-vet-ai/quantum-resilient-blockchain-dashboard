import json
import time
import base64
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict

import oqs
import streamlit as st


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("utf-8"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(data) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def get_base64_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def pick_pqc_signature_mechanism() -> str:
    mechs = oqs.get_enabled_sig_mechanisms()

    preferred_prefixes = [
        "ML-DSA",
        "Dilithium",
        "Falcon",
        "SPHINCS",
        "SLH-DSA",
    ]

    for prefix in preferred_prefixes:
        for mech in mechs:
            if mech.startswith(prefix):
                return mech

    if not mechs:
        raise RuntimeError("No enabled PQC signature mechanism was found.")

    return mechs[0]


def apply_custom_ui():
    image_path = Path("images/quantum_blockchain_bg.png")

    if image_path.exists():
        bg_base64 = get_base64_image(str(image_path))

        custom_css = f"""
        <style>
        .stApp {{
            background:
                linear-gradient(rgba(3, 8, 20, 0.34), rgba(3, 8, 20, 0.34)),
                url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #ffffff;
        }}

        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}

        h1, h2, h3, h4, h5, h6, label {{
            color: #ffffff !important;
        }}

        p, div, span {{
            color: inherit;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(8, 16, 34, 0.72);
            border-right: 1px solid rgba(120, 180, 255, 0.18);
        }}

        .glass-card {{
            background: rgba(7, 18, 40, 0.46);
            border: 1px solid rgba(120, 180, 255, 0.20);
            border-radius: 20px;
            padding: 22px;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.22);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            margin-bottom: 20px;
        }}

        .hero-box {{
            background: rgba(7, 18, 40, 0.40);
            border: 1px solid rgba(120, 180, 255, 0.20);
            border-radius: 24px;
            padding: 32px 28px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            margin-bottom: 24px;
        }}

        .hero-title {{
            font-size: 2.2rem;
            font-weight: 800;
            color: #f4f8ff !important;
            margin-bottom: 0.5rem;
        }}

        .hero-subtitle {{
            font-size: 1.05rem;
            color: #dbe8ff !important;
            line-height: 1.7;
        }}

        .metric-mini {{
            background: rgba(10, 24, 50, 0.42);
            border: 1px solid rgba(120, 180, 255, 0.18);
            border-radius: 18px;
            padding: 16px;
            text-align: center;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
        }}

        .metric-value {{
            font-size: 1.2rem;
            font-weight: 800;
            color: #ffffff !important;
            word-break: break-word;
        }}

        .metric-label {{
            font-size: 0.9rem;
            color: #cddfff !important;
            margin-top: 8px;
        }}

        .step-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            background: linear-gradient(90deg, #0d5eff, #1aa3ff);
            color: #ffffff !important;
            font-weight: 800;
            font-size: 0.85rem;
            margin-bottom: 10px;
        }}

        .step-help {{
            color: #d9e8ff !important;
            font-size: 0.98rem;
            line-height: 1.7;
            margin-bottom: 14px;
        }}

        .stButton > button {{
            width: 100%;
            border-radius: 14px;
            border: 1px solid rgba(120, 180, 255, 0.25);
            background: linear-gradient(90deg, #0d5eff, #1aa3ff);
            color: white !important;
            font-weight: 700;
            padding: 0.8rem 1rem;
            box-shadow: 0 4px 16px rgba(13, 94, 255, 0.25);
        }}

        .stButton > button:hover {{
            border: 1px solid rgba(180, 220, 255, 0.45);
            filter: brightness(1.06);
        }}

        .stNumberInput input,
        .stTextInput input,
        .stTextArea textarea {{
            background-color: rgba(255, 255, 255, 0.94) !important;
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
            caret-color: #111111 !important;
            border-radius: 12px !important;
        }}

        .stNumberInput input::placeholder,
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {{
            color: #666666 !important;
            -webkit-text-fill-color: #666666 !important;
        }}

        .stSelectbox [data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.94) !important;
            border-radius: 12px !important;
            color: #111111 !important;
        }}

        .stSelectbox [data-baseweb="select"] * {{
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
        }}

        .stSelectbox [data-baseweb="select"] input {{
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
        }}

        .stSelectbox div[data-baseweb="select"] span {{
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
        }}

        .stSelectbox svg {{
            fill: #333333 !important;
            color: #333333 !important;
        }}

        div[role="listbox"] {{
            background: rgba(255, 255, 255, 0.98) !important;
            color: #111111 !important;
        }}

        div[role="option"] {{
            background: rgba(255, 255, 255, 0.98) !important;
            color: #111111 !important;
        }}

        div[role="option"] * {{
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
        }}

        div[data-testid="stDataFrame"] {{
            background: rgba(255, 255, 255, 0.90);
            border-radius: 16px;
            overflow: hidden;
        }}

        div[data-testid="stDataFrame"] * {{
            color: #111111 !important;
        }}

        [data-testid="stTextArea"] textarea {{
            background: rgba(255, 255, 255, 0.96) !important;
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
            border-radius: 14px !important;
        }}

        [data-testid="stAlertContainer"] {{
            border-radius: 14px;
        }}

        div[data-testid="stMarkdownContainer"] p {{
            color: #eef4ff !important;
        }}

        hr {{
            border-color: rgba(120, 180, 255, 0.18);
        }}
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)
    else:
        st.warning("Background image not found: images/quantum_blockchain_bg.png")


class PQWallet:
    def __init__(self, mechanism: str):
        self.mechanism = mechanism
        signer = oqs.Signature(self.mechanism)
        self.public_key = signer.generate_keypair()
        self.secret_key = signer.export_secret_key()

    def address(self) -> str:
        return sha256_text(b64e(self.public_key))

    def sign_transaction(self, tx_payload: dict) -> str:
        message = canonical_json(tx_payload).encode("utf-8")
        with oqs.Signature(self.mechanism, secret_key=self.secret_key) as signer:
            signature = signer.sign(message)
        return b64e(signature)

    def export_public_key(self) -> str:
        return b64e(self.public_key)


@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    public_key: str
    signature: str = ""

    def payload(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "public_key": self.public_key,
        }

    def tx_hash(self) -> str:
        return sha256_text(canonical_json(self.payload()))


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list
    previous_hash: str
    nonce: int = 0
    block_hash: str = ""

    def compute_hash(self) -> str:
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        return sha256_text(canonical_json(block_data))


class PQBlockchain:
    def __init__(self, mechanism: str):
        self.mechanism = mechanism
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0" * 64,
            nonce=0,
        )
        genesis.block_hash = genesis.compute_hash()
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def verify_transaction(self, tx: Transaction) -> bool:
        try:
            public_key_bytes = b64d(tx.public_key)
            signature_bytes = b64d(tx.signature)
            message = canonical_json(tx.payload()).encode("utf-8")

            derived_sender = sha256_text(tx.public_key)
            if tx.sender != derived_sender:
                return False

            with oqs.Signature(self.mechanism) as verifier:
                return verifier.verify(message, signature_bytes, public_key_bytes)
        except Exception:
            return False

    def add_block(self, txs: list[Transaction]) -> bool:
        for tx in txs:
            if not self.verify_transaction(tx):
                return False

        tx_dicts = [asdict(tx) for tx in txs]
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=tx_dicts,
            previous_hash=self.last_block.block_hash,
            nonce=0,
        )
        block.block_hash = block.compute_hash()
        self.chain.append(block)
        return True

    def is_chain_valid(self) -> tuple[bool, str]:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            recalculated_hash = current.compute_hash()
            if current.block_hash != recalculated_hash:
                return False, f"Block {i} hash mismatch"

            if current.previous_hash != previous.block_hash:
                return False, f"Block {i} previous_hash mismatch"

            for tx_data in current.transactions:
                tx = Transaction(**tx_data)
                if not self.verify_transaction(tx):
                    return False, f"Invalid signature inside block {i}"
        return True, "The chain is valid."

    def to_display_data(self):
        rows = []
        for block in self.chain:
            rows.append(
                {
                    "index": block.index,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block.timestamp)),
                    "tx_count": len(block.transactions),
                    "previous_hash": block.previous_hash[:20] + "...",
                    "block_hash": block.block_hash[:20] + "...",
                }
            )
        return rows


def init_state():
    if "initialized" in st.session_state:
        return

    mechanism = pick_pqc_signature_mechanism()
    st.session_state.mechanism = mechanism
    st.session_state.blockchain = PQBlockchain(mechanism)

    st.session_state.wallets = {}
    for name in ["Alice", "Bob", "Charlie"]:
        wallet = PQWallet(mechanism)
        st.session_state.wallets[name] = {
            "wallet": wallet,
            "address": wallet.address(),
            "public_key": wallet.export_public_key(),
        }

    st.session_state.pending_txs = []
    st.session_state.initialized = True


def reset_all():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]
    init_state()


st.set_page_config(page_title="PQC Blockchain Demo", layout="wide")
apply_custom_ui()
init_state()

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">PQC Blockchain Demo</div>
        <div class="hero-subtitle">
            A hands-on mini blockchain dashboard for post-quantum signatures, transactions,
            block creation, chain validation, and tampering experiments.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='metric-mini'><div class='metric-value'>{st.session_state.mechanism}</div><div class='metric-label'>Signature Algorithm</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-mini'><div class='metric-value'>{len(st.session_state.blockchain.chain)}</div><div class='metric-label'>Block Count</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-mini'><div class='metric-value'>{len(st.session_state.pending_txs)}</div><div class='metric-label'>Pending Transactions</div></div>", unsafe_allow_html=True)
with m4:
    if st.button("Reset Demo"):
        reset_all()
        st.rerun()

st.divider()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("Wallet List")
wallet_rows = []
for name, info in st.session_state.wallets.items():
    wallet_rows.append(
        {
            "name": name,
            "address": info["address"],
            "public_key_preview": info["public_key"][:60] + "...",
        }
    )
st.dataframe(wallet_rows, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="step-badge">STEP 1</div>', unsafe_allow_html=True)
st.subheader("Create a Transaction")
st.markdown('<div class="step-help">Select a sender, a receiver, and an amount. Then create a signed transaction.</div>', unsafe_allow_html=True)

sender_name = st.selectbox("Sender", list(st.session_state.wallets.keys()), index=0)
receiver_candidates = [x for x in st.session_state.wallets.keys() if x != sender_name]
receiver_name = st.selectbox("Receiver", receiver_candidates, index=0)
amount = st.number_input("Amount", min_value=0.1, value=10.0, step=0.5)

if st.button("Sign and Add to Pending Queue"):
    sender_wallet = st.session_state.wallets[sender_name]["wallet"]
    sender_address = st.session_state.wallets[sender_name]["address"]
    receiver_address = st.session_state.wallets[receiver_name]["address"]
    public_key = st.session_state.wallets[sender_name]["public_key"]

    tx = Transaction(
        sender=sender_address,
        receiver=receiver_address,
        amount=float(amount),
        public_key=public_key,
    )
    tx.signature = sender_wallet.sign_transaction(tx.payload())
    st.session_state.pending_txs.append(asdict(tx))
    st.success("The signed transaction has been added to the pending queue.")
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="step-badge">STEP 2</div>', unsafe_allow_html=True)
st.subheader("Review Pending Transactions and Add a Block")
st.markdown('<div class="step-help">If the transaction appears below, package it into a new block.</div>', unsafe_allow_html=True)

if st.session_state.pending_txs:
    preview_rows = []
    for i, tx in enumerate(st.session_state.pending_txs, start=1):
        preview_rows.append(
            {
                "no": i,
                "sender": tx["sender"][:18] + "...",
                "receiver": tx["receiver"][:18] + "...",
                "amount": tx["amount"],
                "signature_preview": tx["signature"][:40] + "...",
            }
        )
    st.dataframe(preview_rows, use_container_width=True)
else:
    st.info("There is no pending transaction right now.")

if st.button("Create a New Block from Pending Transactions"):
    if not st.session_state.pending_txs:
        st.warning("No pending transaction is available.")
    else:
        tx_objects = [Transaction(**tx) for tx in st.session_state.pending_txs]
        ok = st.session_state.blockchain.add_block(tx_objects)
        if ok:
            st.session_state.pending_txs = []
            st.success("A new block has been added to the chain.")
        else:
            st.error("The block could not be added because at least one transaction is invalid.")
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="step-badge">STEP 3</div>', unsafe_allow_html=True)
st.subheader("Validate the Chain")
st.markdown('<div class="step-help">Check whether the current blockchain structure is still valid.</div>', unsafe_allow_html=True)

if st.button("Run Chain Validation"):
    valid, msg = st.session_state.blockchain.is_chain_valid()
    if valid:
        st.success(msg)
    else:
        st.error(msg)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="step-badge">STEP 4</div>', unsafe_allow_html=True)
st.subheader("Blockchain Summary")
st.markdown('<div class="step-help">Review all generated blocks, then choose a block index to inspect the full JSON payload.</div>', unsafe_allow_html=True)

st.dataframe(st.session_state.blockchain.to_display_data(), use_container_width=True)

st.subheader("Block Detail")
block_index = st.number_input(
    "Block index to inspect",
    min_value=0,
    max_value=max(0, len(st.session_state.blockchain.chain) - 1),
    value=0,
    step=1,
)

selected_block = st.session_state.blockchain.chain[int(block_index)]
block_json_str = json.dumps(
    {
        "index": selected_block.index,
        "timestamp": selected_block.timestamp,
        "transactions": selected_block.transactions,
        "previous_hash": selected_block.previous_hash,
        "nonce": selected_block.nonce,
        "block_hash": selected_block.block_hash,
    },
    ensure_ascii=False,
    indent=2,
)

st.text_area(
    "Block JSON",
    value=block_json_str,
    height=320,
    disabled=True,
)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="step-badge">STEP 5</div>', unsafe_allow_html=True)
st.subheader("Tampering Experiment")
st.markdown('<div class="step-help">Change the amount inside the first real transaction and see how blockchain integrity breaks.</div>', unsafe_allow_html=True)

if st.button("Tamper with the First Real Transaction"):
    if len(st.session_state.blockchain.chain) < 2:
        st.warning("Only the genesis block exists. Create a transaction and add a block first.")
    else:
        target_block = st.session_state.blockchain.chain[1]
        if not target_block.transactions:
            st.warning("Block 1 does not contain any transaction.")
        else:
            target_block.transactions[0]["amount"] = 9999.0
            st.error("The transaction amount has been forcefully changed to 9999.0. Run chain validation again.")
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="step-badge">STEP 6</div>', unsafe_allow_html=True)
st.subheader("Usage Summary")
st.markdown(
    """
    1. Create a signed transaction in **STEP 1**.  
    2. Review it and package it into a block in **STEP 2**.  
    3. Check whether the chain is valid in **STEP 3**.  
    4. Inspect block summaries and raw JSON data in **STEP 4**.  
    5. Tamper with a transaction in **STEP 5**, then run validation again to see integrity failure.
    """
)
st.markdown('</div>', unsafe_allow_html=True)
