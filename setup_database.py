#!/usr/bin/env python3
"""
Script to populate the vector database with product data.
Run this script if you're getting "no product information available" errors.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """Check if all required environment variables are set."""
    load_dotenv()
    
    required_vars = ["GOOGLE_API_KEY", "ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "ASTRA_DB_KEYSPACE"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file with your credentials.")
        print("   You can use .env.template as a reference.")
        return False
    
    print("✅ All environment variables are set.")
    return True

def populate_database():
    """Populate the vector database with product data."""
    try:
        from data_ingestion.ingestion_pipeline import DataIngestion
        
        print("🚀 Starting data ingestion...")
        ingestion = DataIngestion()
        ingestion.run_pipeline()
        print("✅ Database populated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during data ingestion: {str(e)}")
        return False

def test_retriever():
    """Test if the retriever can find documents."""
    try:
        from retriever.retrieval import Retriever
        
        print("🔍 Testing retriever...")
        retriever_obj = Retriever()
        test_query = "Can you suggest good budget laptops?"
        results = retriever_obj.call_retriever(test_query)
        
        print(f"✅ Retriever test successful! Found {len(results)} documents.")
        if results:
            print(f"📄 Sample result: {results[0].page_content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Retriever test failed: {str(e)}")
        return False

def main():
    """Main function to set up the customer support chatbot."""
    print("🤖 Customer Support Chatbot Setup")
    print("=" * 40)
    
    # Step 1: Check environment
    if not check_environment():
        print("\n🛑 Setup failed. Please configure your environment variables.")
        return
    
    # Step 2: Populate database
    print("\n📊 Populating vector database...")
    if not populate_database():
        print("\n🛑 Setup failed. Could not populate database.")
        return
    
    # Step 3: Test retriever
    print("\n🧪 Testing retriever functionality...")
    if not test_retriever():
        print("\n⚠️  Warning: Retriever test failed, but database was populated.")
        print("   You may still be able to use the chatbot.")
    
    print("\n🎉 Setup complete! Your chatbot should now have product information.")
    print("💡 You can now run: uvicorn main:app --reload")

if __name__ == "__main__":
    main()
