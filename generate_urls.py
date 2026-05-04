def generate():
    wikipedia_topics = [
        "Python_(programming_language)", "Artificial_intelligence", "Machine_learning", 
        "Concurrency_(computer_science)", "Web_scraping", "Asynchronous_I/O", 
        "Multi-core_processor", "Software_architecture", "Database", "Cloud_computing"
    ]
    base = "https://en.wikipedia.org/wiki/"
    
    # 10 file
    urls_10 = [base + t for t in wikipedia_topics]
    with open("test_10.txt", "w") as f:
        f.write("\n".join(urls_10))
        
    # 50 file
    with open("test_50.txt", "w") as f:
        f.write("\n".join(urls_10 * 5))
        
    # 100 file
    with open("test_100.txt", "w") as f:
        f.write("\n".join(urls_10 * 10))
        
    print("Successfully generated test_10.txt, test_50.txt, and test_100.txt datasets!")

if __name__ == "__main__":
    generate()
