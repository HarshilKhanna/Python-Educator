import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/activity.dart';
import 'auth_service.dart';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000';

  /// Build headers with the current auth token.
  ///
  /// Throws an [AuthException] if there is no token stored (not logged in).
  Future<Map<String, String>> _authHeaders() async {
    final token = await authService.getToken();
    if (token == null) {
      throw AuthException('Not authenticated. Please log in.');
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<List<Activity>> fetchActivities(String topicId) async {
    // Activities endpoint is auth-guarded — attach token
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

  /// Submit an answer for the currently authenticated student.
  ///
  /// student_id is NO LONGER a parameter — the backend derives it from the JWT.
  Future<double> submitAnswer({
    required String activityId,
    required String submittedAnswer,
  }) async {
    final headers = await _authHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/answer'),
      headers: headers,
      body: jsonEncode({
        // student_id intentionally omitted — server derives it from the token
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
}

/// Thrown when a request fails due to authentication/authorization issues.
class AuthException implements Exception {
  final String message;
  const AuthException(this.message);

  @override
  String toString() => 'AuthException: $message';
}

final apiClient = ApiClient();
