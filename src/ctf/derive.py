from web3 import Web3

def _ensure_0x_prefix(value: str) -> str:
    """Ensure the hex string has 0x prefix."""
    if value and isinstance(value, str) and not value.startswith("0x"):
        return "0x" + value
    return value

def compute_condition_id(oracle: str, question_id: str, outcome_slot_count: int) -> str:
    """
    Computes the condition ID for a given oracle, question ID, and outcome slot count.
    
    Args:
        oracle (str): The address of the oracle contract.
        question_id (str): The unique identifier for the question (bytes32 hex string).
        outcome_slot_count (int): The number of outcome slots (e.g., 2 for binary).

    Returns:
        str: The computed condition ID as a hex string.
    """
    return Web3.solidity_keccak(
        ['address', 'bytes32', 'uint256'],
        [oracle, _ensure_0x_prefix(question_id), outcome_slot_count]
    ).hex()

def compute_collection_id(parent_collection_id: str, condition_id: str, index_set: int) -> str:
    """
    Computes the collection ID for a given parent collection ID, condition ID, and index set.
    
    Args:
        parent_collection_id (str): The parent collection ID (bytes32 hex string). 
                                    Usually bytes32(0) for base conditions.
        condition_id (str): The condition ID (bytes32 hex string).
        index_set (int): The index set representing the outcome slot(s) (e.g., 1 for YES, 2 for NO).

    Returns:
        str: The computed collection ID as a hex string.
    """
    return Web3.solidity_keccak(
        ['bytes32', 'bytes32', 'uint256'],
        [_ensure_0x_prefix(parent_collection_id), _ensure_0x_prefix(condition_id), index_set]
    ).hex()

def compute_position_id(collateral_token: str, collection_id: str) -> str:
    """
    Computes the position ID (Token ID) for a given collateral token and collection ID.
    
    Args:
        collateral_token (str): The address of the collateral token (e.g., USDC).
        collection_id (str): The collection ID (bytes32 hex string).

    Returns:
        str: The computed position ID as a hex string.
    """
    return Web3.solidity_keccak(
        ['address', 'bytes32'],
        [collateral_token, _ensure_0x_prefix(collection_id)]
    ).hex()

def derive_binary_positions(oracle: str, question_id: str, condition_id: str = None, collateral_token: str = None) -> dict:
    """
    Helper to derive YES and NO position IDs for a standard binary market.
    
    Args:
        oracle (str): Oracle address.
        question_id (str): Question ID (bytes32 hex string).
        condition_id (str, optional): If already known, can be passed to skip re-computation.
        collateral_token (str, optional): Collateral token address. 
                                          Defaults to Polymarket USDC.e if not provided.

    Returns:
        dict: containing 'conditionId', 'yesTokenId', 'noTokenId'
    """
    # Polymarket USDC.e address on Polygon
    if collateral_token is None:
        collateral_token = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

    if condition_id is None:
        condition_id = compute_condition_id(oracle, question_id, 2)
    
    # Parent collection is 0x0
    parent_collection_id = "0x" + "0" * 64

    # Binary Market: Slot 1 (IndexSet 1) is YES, Slot 2 (IndexSet 2) is NO
    # Wait, strictly speaking:
    # Polymarket Binary: 
    #  - Outcome 0 (Low index) => IndexSet 1 (0b01) => Usually "YES" (depends on market phrasing, but technically outcome 0)
    #  - Outcome 1 (High index) => IndexSet 2 (0b10) => Usually "NO"
    # Actually, Gnosis CTF docs usually treat index sets bitmask.
    # Slot 0 -> 1 << 0 = 1
    # Slot 1 -> 1 << 1 = 2
    # In Polymarket context:
    #  YES is usually index 0? Or NO?
    #  Let's check stage1.md description:
    #  "YES 头寸的 indexSet = 1 (0b01)... NO 头寸的 indexSet = 2 (0b10)"
    #  Okay, we will follow that.
    
    collection_id_yes = compute_collection_id(parent_collection_id, condition_id, 1)
    collection_id_no = compute_collection_id(parent_collection_id, condition_id, 2)
    
    yes_token_id = compute_position_id(collateral_token, collection_id_yes)
    no_token_id = compute_position_id(collateral_token, collection_id_no)
    
    return {
        "conditionId": condition_id,
        "yesTokenId": yes_token_id,
        "noTokenId": no_token_id
    }
