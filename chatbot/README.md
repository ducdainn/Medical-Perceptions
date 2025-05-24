# ReViCARE Chatbot - Medication Recommendation System

## Overview

The ReViCARE chatbot has been enhanced with a sophisticated medication recommendation system that provides users with:

1. **Symptom-based medication recommendations**: Users can ask what medications are recommended for specific symptoms
2. **Inventory checking**: Users can check if recommended medications are available in the pharmacy inventory
3. **Seamless conversation flow**: The system maintains context between medication recommendations and inventory queries

## Key Features

### Symptom Detection

- Extracts symptoms from user queries using both direct matching and pattern recognition
- Supports common Vietnamese symptoms like "ho" (cough), "sốt" (fever), "đau đầu" (headache)
- Handles complex queries with multiple symptoms

### Medication Recommendation

- Uses the Gemini API to provide evidence-based medication recommendations
- Includes appropriate medical disclaimers and safety information
- Extracts medication names from AI responses for future reference

### Inventory Integration

- Maintains conversation context about previously mentioned medications
- Detects follow-up inventory queries about recommended medications
- Searches pharmacy inventory for exact and similar medications
- Provides detailed inventory information (quantity, price, expiry date)

### Error Handling

- Gracefully handles database errors and missing fields
- Provides appropriate fallback responses when medications aren't found
- Limits result size to avoid overwhelming responses

## Usage Examples

### Example 1: Medication Recommendation

**User**: "Tôi bị ho, nên uống thuốc gì?" (I have a cough, what medicine should I take?)

**System**: 
- Detects "ho" (cough) as the symptom
- Provides medication recommendations like Dextromethorphan, Guaifenesin
- Includes usage information and safety warnings

### Example 2: Inventory Follow-up

**User**: "Nhà thuốc có những loại thuốc này không?" (Does the pharmacy have these medications?)

**System**:
- Recognizes this as an inventory query about previously mentioned medications
- Searches inventory for each medication
- Returns availability, price, and other relevant information

## Implementation Details

The implementation includes:

1. **Symptom extraction functions**:
   - `extract_symptom_from_medication_query`: Extracts symptoms from medication queries
   - `extract_symptom_list`: Extracts multiple symptoms from diagnostic queries

2. **Medication recommendation functions**:
   - `check_if_medication_recommendation_query`: Detects medication recommendation queries
   - `process_medication_recommendation_query`: Gets recommendations from Gemini API
   - `extract_medication_names_from_response`: Extracts medication names from AI responses

3. **Inventory query functions**:
   - `check_if_inventory_query_about_medicine`: Detects inventory follow-up queries
   - `get_medication_inventory_info`: Gets inventory information for medications
   - `search_medication_in_inventory`: Searches for exact medication matches
   - `fuzzy_search_medication`: Searches for similar medications

4. **Context management**:
   - Uses ChatMemory model to maintain conversation context
   - Tracks mentioned medications and symptoms for follow-up queries

## Technical Notes

- The system uses regex patterns to identify medication queries and extract symptoms
- Medication names are extracted from AI responses using pattern matching and common medication lists
- Inventory queries use both exact and fuzzy matching to find medications
- Results are deduplicated and limited to avoid overwhelming responses 