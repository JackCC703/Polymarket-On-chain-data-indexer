import argparse
import json
import os
from src.trade_decoder import decode_trades
from src.market_decoder import decode_market

def main():
    parser = argparse.ArgumentParser(description="Polymarket Indexer Stage 1 Demo")
    parser.add_argument("--tx-hash", required=True, help="Transaction Hash")
    parser.add_argument("--event-slug", help="Market/Event Slug for API Lookup")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    output_data = {}
    
    # 1. Decode Trades
    print(f"Decoding trades for tx: {args.tx_hash}...")
    try:
        trades = decode_trades(args.tx_hash)
        output_data['tx_hash'] = args.tx_hash
        output_data['trades'] = trades
        print(f"Found {len(trades)} trades.")
    except Exception as e:
        print(f"Error decoding trades: {e}")
        output_data['trades_error'] = str(e)

    # 2. Decode Market
    if args.event_slug:
        print(f"Decoding market for slug: {args.event_slug}...")
        try:
            market_info = decode_market(slug=args.event_slug)
            output_data['market'] = market_info
            
            # 3. Cross-Validation (Optional)
            # Check if trade tokens match market tokens
            if 'trades' in output_data and output_data['trades']:
                trade_tokens = set(t['token_id'] for t in output_data['trades'])
                yes_id = market_info.get('yesTokenId')
                no_id = market_info.get('noTokenId')
                
                print("Verifying tokens...")
                for t in trade_tokens:
                    if t == yes_id:
                        print(f"  Token {t} matches YES token.")
                    elif t == no_id:
                        print(f"  Token {t} matches NO token.")
                    else:
                        print(f"  Token {t} DOES NOT match market YES/NO tokens (might be another market in same tx).")
                        
        except Exception as e:
             print(f"Error decoding market: {e}")
             output_data['market_error'] = str(e)
    
    # Final Output
    final_json = {"stage1": output_data}
    print(json.dumps(final_json, indent=2))
    
    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(final_json, f, indent=2)
        print(f"Output saved to {args.output}")

if __name__ == "__main__":
    main()
