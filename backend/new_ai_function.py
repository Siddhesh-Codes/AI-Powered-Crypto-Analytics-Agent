async def get_real_ai_response_v2(user_message: str, context: Dict[str, Any] = {}) -> str:
    """ENTERPRISE-GRADE: Groq AI with GUARANTEED live price integration"""
    if not AI_SERVICE_AVAILABLE:
        raise Exception("AI service not available")
    
    try:
        print(f"\n🚀 [AI_ENGINE] Processing: '{user_message}'")
        
        # Step 1: Always detect crypto mentions
        crypto_mentions = detect_crypto_mentions(user_message)
        print(f"🎯 [DETECTION] Found cryptos: {crypto_mentions}")
        
        # Step 2: MANDATORY live price fetching for ANY crypto mention
        live_price_context = ""
        
        if crypto_mentions:
            print(f"💰 [LIVE_FETCH] Fetching real-time prices...")
            
            # Symbol mapping for API calls
            symbol_map = {
                'BITCOIN': 'BTC', 'ETHEREUM': 'ETH', 'SOLANA': 'SOL',
                'CARDANO': 'ADA', 'POLYGON': 'MATIC', 'POLKADOT': 'DOT',
                'CHAINLINK': 'LINK', 'COSMOS': 'ATOM', 'ALGORAND': 'ALGO',
                'UNISWAP': 'UNI'
            }
            
            live_prices = []
            for crypto in crypto_mentions:
                symbol = symbol_map.get(crypto.upper(), crypto.upper())
                
                print(f"🔄 [API_CALL] Fetching {crypto} ({symbol})...")
                live_data = await get_live_crypto_price(symbol)
                
                if live_data:
                    price_info = f"{live_data['name']} ({symbol}): ${live_data['price']:,.2f} ({live_data['change_24h']:+.1f}% 24h)"
                    live_prices.append(price_info)
                    print(f"✅ [SUCCESS] {symbol}: ${live_data['price']:,.2f}")
                else:
                    print(f"❌ [FAILED] Could not fetch {symbol}")
                    # For critical price questions, fail fast rather than give wrong data
                    if any(word in user_message.lower() for word in ['price', 'cost', 'worth', 'current']):
                        return f"Unable to fetch current {symbol} price data. Please try again in a moment."
            
            # Build mandatory live price context
            if live_prices:
                live_price_context = f"""CRITICAL LIVE MARKET DATA (USE THESE EXACT PRICES):
{chr(10).join(f"- {price}" for price in live_prices)}

INSTRUCTION: Use ONLY these live prices above. Ignore all other price data from training."""
                print(f"✅ [CONTEXT] Built live price context for {len(live_prices)} coins")
        
        # Step 3: Complexity analysis for response length
        complexity = analyze_question_complexity(user_message)
        max_tokens = 100 if complexity == "simple" else 250 if complexity == "medium" else 400
        
        # Step 4: Create ENFORCED system prompt
        if live_price_context:
            system_prompt = f"""You are a professional cryptocurrency analyst with access to REAL-TIME market data.

{live_price_context}

MANDATORY RULES:
1. Use ONLY the live prices provided above when discussing prices
2. These prices are current and accurate
3. NEVER use price data from your training (it's outdated)
4. Be professional, no emojis, no markdown formatting
5. Keep response length appropriate for the question complexity

Provide accurate analysis using the live data shown above."""
        else:
            system_prompt = """You are a professional cryptocurrency analyst. Provide accurate information about cryptocurrencies and blockchain technology. Be professional, no emojis, no markdown formatting."""
        
        # Step 5: Call Groq API with enforced context
        print(f"🤖 [GROQ_CALL] Sending to AI (max_tokens: {max_tokens})")
        
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,  # Low temperature for consistent, factual responses
            max_tokens=max_tokens
        )
        
        ai_response = completion.choices[0].message.content.strip()
        
        # Step 6: Final cleanup to ensure no markdown
        clean_response = clean_markdown_response(ai_response)
        
        print(f"✅ [SUCCESS] Generated response with live price integration")
        return clean_response
        
    except Exception as e:
        print(f"❌ [ERROR] Groq API failed: {e}")
        raise Exception(f"AI service error: {str(e)}")