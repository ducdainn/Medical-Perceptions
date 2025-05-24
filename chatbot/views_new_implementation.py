@csrf_exempt
@login_required
def bot_send_message(request):
    """
    API endpoint for sending messages to the chatbot and getting AI-generated responses
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        reset_context = data.get('reset_context', False)
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create user's memory object for context
        chat_memory, created = ChatMemory.objects.get_or_create(user=request.user)
        
        # Reset context if requested
        if reset_context:
            chat_memory.clear_context()
        
        # Save user message
        user_msg = BotMessage.objects.create(
            user=request.user,
            type='user',
            content=user_message
        )
        
        # Add to memory context
        chat_memory.add_message('user', user_message)
        
        # First check if this is an inventory query
        if any(keyword in user_message.lower() for keyword in ['thuốc', 'kho', 'tồn kho', 'inventory', 'còn hàng', 'hết hàng']):
            inventory_response = AdvancedChatbotDataAccess.process_inventory_query(user_message)
            if inventory_response:
                # Save bot response
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=inventory_response
                )
                # Add to memory
                chat_memory.add_message('bot', inventory_response)
                return JsonResponse({
                    'message': inventory_response,
                    'type': 'bot',
                    'query_type': 'inventory'
                })
        
        # Check for medical knowledge queries (symptoms, diseases)
        if check_if_medical_query(user_message):
            # Extract search terms
            search_term = extract_search_term(user_message)
            if search_term:
                database_response = process_medical_query(user_message)
                if database_response and "Không tìm thấy thông tin liên quan" not in database_response:
                    # Save bot response
                    bot_msg = BotMessage.objects.create(
                        user=request.user,
                        type='bot',
                        content=database_response
                    )
                    # Add to memory
                    chat_memory.add_message('bot', database_response)
                    return JsonResponse({
                        'message': database_response,
                        'type': 'bot',
                        'query_type': 'medical'
                    })
        
        # Check for symptom diagnosis query
        symptom_list = extract_symptom_list(user_message)
        if len(symptom_list) >= 2:
            diagnosis_response = AdvancedChatbotDataAccess.process_advanced_diagnosis(symptom_list)
            if diagnosis_response and "Không tìm thấy bệnh" not in diagnosis_response:
                # Save bot response
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=diagnosis_response
                )
                # Add to memory
                chat_memory.add_message('bot', diagnosis_response)
                return JsonResponse({
                    'message': diagnosis_response,
                    'type': 'bot',
                    'query_type': 'diagnosis'
                })
        
        # If we've got here, we couldn't handle the query with database knowledge
        # Try using Gemini API for general knowledge response
        if GEMINI_API_KEY:
            # Get conversation context for AI prompt
            conversation_context = chat_memory.get_context_for_prompt()
            
            # Prepare context for the AI
            system_info = """
            Bạn là trợ lý chăm sóc sức khỏe tự động của ReViCARE - một hệ thống quản lý phòng khám.
            Hãy trả lời câu hỏi y tế dựa trên kiến thức chuyên môn của bạn.
            Trả lời bằng tiếng Việt, ngắn gọn và chính xác.
            Nếu không chắc chắn về thông tin, hãy cho biết giới hạn của mình và đề xuất người dùng 
            tham khảo ý kiến bác sĩ hoặc chuyên gia y tế.
            
            Chú ý: KHÔNG sử dụng ký tự * trong câu trả lời của bạn. Thay vì dùng dấu * để đánh dấu điểm, hãy dùng dấu • hoặc -.
            """
            
            # Prepare prompt for Gemini AI
            prompt = f"{system_info}\n\n{conversation_context}\n\nCâu hỏi: {user_message}"
            
            try:
                # Call the Gemini API
                response = requests.post(
                    f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 1024,
                        }
                    }
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    ai_response = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    
                    if ai_response:
                        # Clean any markdown formatting
                        ai_response = clean_markdown(ai_response)
                        
                        # Save bot response
                        bot_msg = BotMessage.objects.create(
                            user=request.user,
                            type='bot',
                            content=ai_response
                        )
                        
                        # Add to memory context
                        chat_memory.add_message('bot', ai_response)
                        
                        return JsonResponse({
                            'message': ai_response,
                            'type': 'bot',
                            'query_type': 'ai'
                        })
                else:
                    print(f"Gemini API error: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error calling Gemini API: {str(e)}")
        
        # If all else fails or API error occurred, return a generic response
        generic_response = "Tôi không tìm thấy thông tin liên quan đến yêu cầu của bạn. Vui lòng hỏi rõ hơn hoặc liên hệ với nhân viên y tế để được hỗ trợ trực tiếp."
        
        # Save bot response
        bot_msg = BotMessage.objects.create(
            user=request.user,
            type='bot',
            content=generic_response
        )
        
        # Add to memory context
        chat_memory.add_message('bot', generic_response)
        
        return JsonResponse({
            'message': generic_response,
            'type': 'bot',
            'query_type': 'generic'
        })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 