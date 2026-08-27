import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class ChatHistoryService {
  static const String _prefix = 'chat_history_';
  static const int _maxMessages = 50;

  /// Load messages for a specific topic
  Future<List<Map<String, dynamic>>> loadHistory(String topicId) async {
    final prefs = await SharedPreferences.getInstance();
    final key = '$_prefix$topicId';
    final jsonString = prefs.getString(key);
    
    if (jsonString == null) return [];
    
    try {
      final List<dynamic> decoded = jsonDecode(jsonString);
      return decoded.map((e) => e as Map<String, dynamic>).toList();
    } catch (e) {
      return [];
    }
  }

  /// Save messages for a specific topic
  Future<void> saveHistory(String topicId, List<Map<String, dynamic>> messages) async {
    final prefs = await SharedPreferences.getInstance();
    final key = '$_prefix$topicId';
    
    // Keep only the last N messages
    final messagesToSave = messages.length > _maxMessages 
        ? messages.sublist(messages.length - _maxMessages) 
        : messages;
        
    await prefs.setString(key, jsonEncode(messagesToSave));
  }

  /// Clear history for a specific topic
  Future<void> clearHistory(String topicId) async {
    final prefs = await SharedPreferences.getInstance();
    final key = '$_prefix$topicId';
    await prefs.remove(key);
  }
}

final chatHistoryService = ChatHistoryService();
