import os
import requests
from pathlib import Path
import time

def download_crypto_logos():
    # Create the directory if it doesn't exist
    static_dir = Path('static/images/crypto')
    static_dir.mkdir(parents=True, exist_ok=True)

    # List of cryptocurrencies with their correct CoinGecko IDs and display names
    cryptocurrencies = {
        'bitcoin': 'bitcoin',
        'ethereum': 'ethereum',
        'tether': 'tether',
        'binancecoin': 'binancecoin',
        'xrp': 'ripple',  # XRP's ID is 'ripple' in CoinGecko
        'cardano': 'cardano',
        'solana': 'solana',
        'polkadot': 'polkadot',
        'dogecoin': 'dogecoin',
        'polygon': 'matic-network'  # Polygon's ID is 'matic-network'
    }

    # Get the coin data from CoinGecko API
    try:
        print("Fetching coin data from CoinGecko...")
        response = requests.get(
            'https://api.coingecko.com/api/v3/coins/markets',
            params={
                'vs_currency': 'usd',
                'ids': ','.join(cryptocurrencies.values()),
                'order': 'market_cap_desc',
                'per_page': 100,
                'page': 1,
                'sparkline': False
            }
        )
        
        if response.status_code == 200:
            coins_data = response.json()
            print(f"Successfully fetched data for {len(coins_data)} coins")
            
            # Download each logo
            for coin in coins_data:
                try:
                    coin_id = coin['id']
                    image_url = coin.get('image')
                    
                    if image_url:
                        print(f"Downloading logo for {coin['name']} ({coin_id})...")
                        img_response = requests.get(image_url)
                        
                        if img_response.status_code == 200:
                            # Find the correct filename from our mapping
                            filename = next((k for k, v in cryptocurrencies.items() if v == coin_id), coin_id)
                            image_path = static_dir / f"{filename}.png"
                            
                            with open(image_path, 'wb') as f:
                                f.write(img_response.content)
                            print(f"✓ Downloaded {coin['name']} logo as {filename}.png")
                        else:
                            print(f"✗ Failed to download {coin['name']} logo: {img_response.status_code}")
                    else:
                        print(f"✗ No image URL found for {coin['name']}")
                        
                    # Add a small delay to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"✗ Error downloading {coin.get('name', 'unknown')} logo: {str(e)}")
        else:
            print(f"✗ Failed to get coin data: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error fetching coin data: {str(e)}")

    # Create a default image if it doesn't exist
    default_image_path = static_dir / 'default.png'
    if not default_image_path.exists():
        try:
            print("\nCreating default image...")
            default_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="16" cy="16" r="16" fill="#F7931A"/>
    <path d="M23.189 14.02c.314-2.096-1.283-3.223-3.465-3.975l.708-2.84-1.728-.43-.69 2.765c-.454-.114-.92-.22-1.385-.326l.695-2.783L15.596 6l-.708 2.839c-.376-.086-.746-.17-1.104-.26l.002-.009-2.384-.595-.46 1.846s1.283.294 1.256.312c.7.175.826.638.805 1.006l-.806 3.235c.048.012.11.03.18.057l-.183-.046-1.13 4.532c-.086.212-.303.531-.793.41.018.026-1.256-.314-1.256-.314l-.858 1.978 2.25.562c.418.105.828.215 1.231.318l-.715 2.872 1.727.43.708-2.84c.472.127.93.245 1.378.357l-.706 2.828 1.728.43.715-2.866c2.948.558 5.164.333 6.097-2.333.752-2.146-.037-3.385-1.588-4.192 1.13-.26 1.98-1.003 2.207-2.538zm-3.95 5.538c-.533 2.147-4.148.986-5.32.695l.95-3.805c1.172.293 4.929.872 4.37 3.11zm.535-5.569c-.487 1.953-3.495.96-4.47.717l.86-3.45c.975.243 4.118.696 3.61 2.733z" fill="white"/>
</svg>'''
            
            with open(default_image_path, 'w') as f:
                f.write(default_svg)
            print("✓ Created default image")
        except Exception as e:
            print(f"✗ Error creating default image: {str(e)}")

if __name__ == '__main__':
    print("Starting cryptocurrency logo download...")
    download_crypto_logos()
    print("\nDownload process completed!") 