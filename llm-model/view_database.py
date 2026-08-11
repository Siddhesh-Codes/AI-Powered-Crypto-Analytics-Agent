"""
Database Viewer - Easy-to-use interface to view training data
Perfect for showing your professor the fetched data!
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    os.system('chcp 65001 > nul')

from database_manager import TrainingDataDB, view_database_contents
import sqlite3

def interactive_menu():
    """Interactive menu to explore database"""
    db = TrainingDataDB()
    
    while True:
        print("\n" + "="*60)
        print("LLM TRAINING DATABASE VIEWER")
        print("="*60)
        print("\nChoose an option:")
        print("  1. View Database Statistics")
        print("  2. View Latest Cryptocurrency Data")
        print("  3. View Latest News Data")
        print("  4. View All Training Sessions")
        print("  5. View Complete Database Contents")
        print("  6. Export Data to CSV")
        print("  0. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "0":
            print("\nGoodbye!")
            db.close()
            break
        
        elif choice == "1":
            db.print_database_stats()
        
        elif choice == "2":
            print("\n" + "="*60)
            print("LATEST CRYPTOCURRENCY DATA")
            print("="*60)
            try:
                limit = int(input("\nHow many records to show? (default 10): ") or "10")
            except:
                limit = 10
            
            crypto_data = db.get_latest_crypto_data(limit)
            if crypto_data:
                for i, record in enumerate(crypto_data, 1):
                    print(f"\n{i}. {record['name']} ({record['symbol']})")
                    print(f"   Price: ${record['price']:,.2f}")
                    print(f"   24h Change: {record['percent_change_24h']:.2f}%")
                    print(f"   Volume: ${record['volume_24h']:,.0f}")
                    print(f"   Market Cap: ${record['market_cap']:,.0f}")
                    print(f"   Fetched: {record['fetched_at']}")
            else:
                print("\n  No data available. Run training first!")
        
        elif choice == "3":
            print("\n" + "="*60)
            print("LATEST NEWS DATA")
            print("="*60)
            try:
                limit = int(input("\nHow many records to show? (default 10): ") or "10")
            except:
                limit = 10
            
            news_data = db.get_latest_news_data(limit)
            if news_data:
                for i, record in enumerate(news_data, 1):
                    print(f"\n{i}. {record['title']}")
                    print(f"   Source: {record['source']}")
                    print(f"   Published: {record['published_at']}")
                    print(f"   URL: {record['url']}")
                    print(f"   Fetched: {record['fetched_at']}")
            else:
                print("\n  No data available. Run training first!")
        
        elif choice == "4":
            print("\n" + "="*60)
            print("ALL TRAINING SESSIONS")
            print("="*60)
            
            sessions = db.get_all_training_sessions()
            if sessions:
                for i, session in enumerate(sessions, 1):
                    print(f"\n{i}. {session['session_name']}")
                    print(f"   Model: {session['model_name']}")
                    print(f"   Status: {session['status']}")
                    print(f"   Epochs: {session['num_epochs']}")
                    print(f"   Batch Size: {session['batch_size']}")
                    print(f"   Learning Rate: {session['learning_rate']}")
                    print(f"   Crypto Records: {session['total_crypto_records']}")
                    print(f"   News Records: {session['total_news_records']}")
                    print(f"   Started: {session['started_at']}")
                    
                    if session['status'] == 'completed':
                        print(f"   Completed: {session['completed_at']}")
                        print(f"   Final Accuracy: {session['final_accuracy']:.2%}")
                        print(f"   Training Loss: {session['final_train_loss']:.4f}")
                        print(f"   Validation Loss: {session['final_val_loss']:.4f}")
                        print(f"   Duration: {session['training_duration']:.2f} seconds")
            else:
                print("\n  No training sessions yet. Run training first!")
        
        elif choice == "5":
            view_database_contents()
        
        elif choice == "6":
            print("\n" + "="*60)
            print("EXPORT DATA TO CSV")
            print("="*60)
            print("\nChoose what to export:")
            print("  1. Cryptocurrency Data")
            print("  2. News Data")
            print("  3. Training Sessions")
            
            export_choice = input("\nEnter your choice (1-3): ").strip()
            
            if export_choice == "1":
                df = db.export_to_dataframe('crypto_data')
                filename = f"exported_crypto_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                print(f"\n[SUCCESS] Exported {len(df)} records to: {filename}")
            
            elif export_choice == "2":
                df = db.export_to_dataframe('news_data')
                filename = f"exported_news_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                print(f"\n[SUCCESS] Exported {len(df)} records to: {filename}")
            
            elif export_choice == "3":
                df = db.export_to_dataframe('training_sessions')
                filename = f"exported_training_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                print(f"\n[SUCCESS] Exported {len(df)} records to: {filename}")
            
            else:
                print("\n  Invalid choice!")
        
        else:
            print("\n  Invalid choice! Please enter 0-6.")
        
        input("\nPress Enter to continue...")
    
    db.close()


if __name__ == "__main__":
    from datetime import datetime
    
    print("\n" + "="*60)
    print("WELCOME TO LLM TRAINING DATABASE VIEWER")
    print("="*60)
    print("\nThis tool lets you view all the data fetched and used")
    print("for training the cryptocurrency analytics LLM model.")
    print("\nDatabase file: crypto_llm_training.db")
    print("="*60)
    
    # Check if database exists
    if not os.path.exists('crypto_llm_training.db'):
        print("\n[WARNING] Database not found!")
        print("Please run the training first: python run_training.py")
        input("\nPress Enter to exit...")
    else:
        interactive_menu()
