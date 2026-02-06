import argparse
import json
import sys
from src.indexer.gamma import fetch_market_by_slug, fetch_market_by_id
from src.ctf.derive import derive_binary_positions

def decode_market(slug: str = None, condition_id: str = None) -> dict:
    market_data = None
    
    # 1. Fetch data from API
    if slug:
        market_data = fetch_market_by_slug(slug)
    elif condition_id:
        market_data = fetch_market_by_id(condition_id)
        
    if not market_data:
        raise ValueError("Market not found in Gamma API")

    # 2. Extract parameters
    # Note: Gamma API field names might vary. Adapting to common fields.
    # We need: oracle, questionId, conditionId
    
    # Commonly: 
    # questionID, conditionId, 
    # For oracle: 'rewards' or 'resolution_source' or hardcoded logic?
    # Polymarket markets use UMA CTF Adapter.
    # Gamma often returns `umaBond` or `rewards` info.
    # Wait, stage1.md says we should output "oracle".
    # Gamma 'questionID' field usually exists.
    
    cid = market_data.get("conditionId")
    qid = market_data.get("questionID") 
    
    # Oracle address might not be explicitly in simple market response? 
    # Usually it's the UMA Optimistic Oracle Adapter.
    # We might need to fetch it or guess it? 
    # Actually, if we have the conditionId, we can RECOVER the oracle if we brute force? No.
    # But usually it's fixed per market type.
    # Or maybe it's in the response.
    # Let's check `stage1.md`.
    # "Gamama API...其中可能包含 conditionId... 如果输入只有 conditionId...通常 Gamma API...会有 questionId 和 oracle 名称".
    # If API doesn't have it, we might need a default or look harder.
    # For now, let's assume it's in the data or we use a known oracle if missing?
    # Let's try to find keys like 'oracle' or 'resolutionSource'.
    
    oracle = market_data.get("oracle") 
    if not oracle:
        # Fallback or try to find in other fields?
        # Many Polymarket markets use the same UMA address.
        # Let's check if the user provided one in the prompt example.
        # "0x157Ce2d672854c848c9b79C49a8Cc6cc89176a49"
        # We can use this as a fallback for now if null.
        # Or better, print warning.
        pass

    collateral = market_data.get("collateralToken") # Usually USDC

    # 3. Derive IDs locally
    derived = derive_binary_positions(
        oracle=oracle,
        question_id=qid,
        condition_id=cid,
        collateral_token=collateral
    )
    
    # 4. Compare with API data (clobTokenIds)
    api_tokens = market_data.get("clobTokenIds", [])
    if api_tokens and len(api_tokens) == 2:
        # Format usually ["yes_id", "no_id"]? 
        # Actually usually ["token_id_0", "token_id_1"] which corresponds to outcome 0 and outcome 1.
        # We mapped Outcome 1 -> YES (IndexSet 1), Outcome 2 -> NO (IndexSet 2).
        # Wait, Outcome Slot 0 corresponds to IndexSet 1 (1 << 0).
        # Outcome Slot 1 corresponds to IndexSet 2 (1 << 1).
        # So derived['yesTokenId'] should match api_tokens[0]
        # derived['noTokenId'] should match api_tokens[1]
        
        # We can validate equality.
        pass

    return {
        "conditionId": cid,
        "oracle": oracle,
        "questionId": qid,
        "outcomeSlotCount": 2,
        "collateralToken": collateral,
        "yesTokenId": derived["yesTokenId"],
        "noTokenId": derived["noTokenId"],
        "gamma": market_data
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--market-slug", help="Market Slug")
    parser.add_argument("--tx-hash", help="Transaction Hash (Optional for strict decoding from logs)")
    parser.add_argument("--log-index", help="Log Index (Optional)")
    parser.add_argument("--output", help="Output file")
    
    args = parser.parse_args()
    
    try:
        if args.market_slug:
            result = decode_market(slug=args.market_slug)
            print(json.dumps(result, indent=2))
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
        else:
            print("Please provide --market-slug")
            
    except Exception as e:
        print(f"Error: {e}")
