import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/activity.dart';
import 'auth_service.dart';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000';

  Future<Map<String, String>> _authHeaders() async {
    final token = await authService.getToken();
    if (token == null) throw AuthException('Not authenticated. Please log in.');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<List<Activity>> fetchActivities(String topicId) async {
    final headers = await _authHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/activities?topic_id=$topicId'),
      headers: headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Activity.fromJson(json)).toList();
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired. Please log in again.');
    } else {
      throw Exception('Failed to load activities: ${response.statusCode}');
    }
  }

  Future<double> submitAnswer({
    required String activityId,
    required String submittedAnswer,
  }) async {
    final headers = await _authHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/answer'),
      headers: headers,
      body: jsonEncode({
        'activity_id': activityId,
        'submitted_answer': submittedAnswer,
      }),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['mastery'] as num).toDouble();
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired. Please log in again.');
    } else {
      throw Exception('Failed to submit answer: ${response.statusCode}');
    }
  }

  /// Send a free-text message to the tutor agent.
  Future<Map<String, dynamic>> tutorChat({
    required String message,
    required String topicId,
  }) async {
    final headers = await _authHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/tutor/interact'),
      headers: headers,
      body: jsonEncode({'message': message, 'topic_id': topicId}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      // Normalise: Flutter expects a 'response' key for display
      if (!data.containsKey('response')) {
        final display = data['answer'] ??
            (data['next_activity_type'] != null
                ? 'Next up: ${data['next_activity_type']} on ${data['next_topic_id']} — ${data['reason'] ?? ''}'
                : 'No response.');
        data['response'] = display;
      }
      return data;
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired. Please log in again.');
    } else {
      throw Exception('Tutor error: ${response.statusCode}');
    }
  }

  /// Fetch per-topic mastery for the current student (decoded from JWT).
  Future<List<Map<String, dynamic>>> fetchMastery() async {
    final headers = await _authHeaders();
    final token = await authService.getToken();
    if (token == null) throw AuthException('Not authenticated.');
    final parts = token.split('.');
    if (parts.length < 2) throw Exception('Malformed token');
    final payload = utf8.decode(
      base64Url.decode(base64Url.normalize(parts[1])),
    );
    final sub =
        (jsonDecode(payload) as Map<String, dynamic>)['sub'] as String;
    final response = await http.get(
      Uri.parse('$baseUrl/students/$sub/mastery'),
      headers: headers,
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return List<Map<String, dynamic>>.from(data['mastery'] ?? []);
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired.');
    } else {
      return [];
    }
  }
}

/// Thrown when a request fails due to authentication/authorization issues.
class AuthException implements Exception {
  final String message;
  const AuthException(this.message);

  @override
  String toString() => 'AuthException: $message';
}

final apiClient = ApiClient();
