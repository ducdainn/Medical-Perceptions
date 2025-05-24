if __name__ == "__main__":
    print("Starting medication recommendation tests...\n")
    test_medication_recommendation_detection()
    test_symptom_extraction()
    test_medication_response()
    try:
        test_rest_api()
    except Exception as e:
        print(f"REST API test failed: {str(e)}")
    print("Test complete.") 