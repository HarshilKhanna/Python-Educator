import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/activity.dart';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000';

  Future<List<Activity>> fetchActivities(String topicId) async {
    final response = await http.get(Uri.parse('$baseUrl/activities?topic_id=$topicId'));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Activity.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load activities: ${response.statusCode}');
    }
  }

  Future<double> submitAnswer({
    required String studentId,
    required String activityId,
    required String submittedAnswer,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/answer'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'student_id': studentId,
        'activity_id': activityId,
        'submitted_answer': submittedAnswer,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['mastery'] as num).toDouble();
    } else {
      throw Exception('Failed to submit answer: ${response.statusCode}');
    }
  }
}

final apiClient = ApiClient();
