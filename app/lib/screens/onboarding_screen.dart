import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../services/auth_service.dart';
import '../config.dart';
import 'home_screen.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  String _explanationPref = 'conceptual'; // 'conceptual' or 'worked_examples'
  String _pacingPref = 'normal'; // 'slower' or 'normal'
  bool _isLoading = false;
  String? _errorMessage;

  String get _baseUrl => backendBaseUrl;

  Future<void> _submit() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final token = await authService.getToken();
      final userId = await authService.getUserId();
      
      if (token == null || userId == null) {
        throw Exception('Not logged in');
      }

      final response = await http.patch(
        Uri.parse('$_baseUrl/students/$userId/style'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'style_profile': {
            'explanation': _explanationPref,
            'pacing': _pacingPref,
          }
        }),
      );

      if (response.statusCode == 200) {
        if (mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const HomeScreen()),
          );
        }
      } else {
        setState(() {
          _errorMessage = 'Failed to save preferences.';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Network error. Try again.';
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Widget _buildSelectionCard({
    required String title,
    required String description,
    required bool isSelected,
    required VoidCallback onTap,
    required IconData icon,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected 
              ? const Color(0xFF6366F1).withValues(alpha: 0.15) 
              : const Color(0xFF141824),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected 
                ? const Color(0xFF6366F1) 
                : const Color(0xFF1F2937),
            width: 1.5,
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: isSelected ? const Color(0xFF6366F1) : const Color(0xFF6B7280),
              size: 28,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: isSelected ? Colors.white : const Color(0xFFE5E7EB),
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: TextStyle(
                      color: isSelected ? const Color(0xFF9CA3AF) : const Color(0xFF6B7280),
                      fontSize: 13,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              const Icon(Icons.check_circle_rounded, color: Color(0xFF6366F1)),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 500),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Welcome to Python Educator',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'To help your AI tutor adapt to you, tell us a bit about how you prefer to learn.',
                    style: TextStyle(
                      color: Color(0xFF94A3B8),
                      fontSize: 15,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 32),

                  const Text(
                    '1. Explanation Style',
                    style: TextStyle(
                      color: Color(0xFFE2E8F0),
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildSelectionCard(
                    title: 'Conceptual',
                    description: 'I prefer understanding the "why" and learning the theory behind concepts first.',
                    icon: Icons.psychology_rounded,
                    isSelected: _explanationPref == 'conceptual',
                    onTap: () => setState(() => _explanationPref = 'conceptual'),
                  ),
                  const SizedBox(height: 12),
                  _buildSelectionCard(
                    title: 'Worked Examples',
                    description: 'I learn best by seeing code examples and applying them directly.',
                    icon: Icons.code_rounded,
                    isSelected: _explanationPref == 'worked_examples',
                    onTap: () => setState(() => _explanationPref = 'worked_examples'),
                  ),

                  const SizedBox(height: 32),

                  const Text(
                    '2. Pacing Preference',
                    style: TextStyle(
                      color: Color(0xFFE2E8F0),
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildSelectionCard(
                    title: 'Normal Pacing',
                    description: 'Move onto new topics as soon as I pass the exercises.',
                    icon: Icons.speed_rounded,
                    isSelected: _pacingPref == 'normal',
                    onTap: () => setState(() => _pacingPref = 'normal'),
                  ),
                  const SizedBox(height: 12),
                  _buildSelectionCard(
                    title: 'Slower Pacing',
                    description: 'I prefer more repetition and practice to make sure I really get it before moving on.',
                    icon: Icons.accessibility_new_rounded,
                    isSelected: _pacingPref == 'slower',
                    onTap: () => setState(() => _pacingPref = 'slower'),
                  ),

                  const SizedBox(height: 40),
                  
                  if (_errorMessage != null) ...[
                    Text(
                      _errorMessage!,
                      style: const TextStyle(color: Color(0xFFEF4444), fontSize: 14),
                    ),
                    const SizedBox(height: 16),
                  ],

                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: FilledButton(
                      onPressed: _isLoading ? null : _submit,
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF6366F1),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: _isLoading 
                          ? const SizedBox(
                              width: 20, height: 20, 
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)
                            )
                          : const Text(
                              'Complete Setup',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
