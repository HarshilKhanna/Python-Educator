import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/login_screen.dart';
import 'screens/activity_screen.dart';
import 'services/auth_service.dart';

void main() {
  runApp(const ProviderScope(child: PythonEducatorApp()));
}

class PythonEducatorApp extends StatelessWidget {
  const PythonEducatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Python Educator',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6366F1),
          brightness: Brightness.dark,
          surface: const Color(0xFF141824),
        ),
        scaffoldBackgroundColor: const Color(0xFF0A0E1A),
        useMaterial3: true,
      ),
      home: const _AuthGate(),
    );
  }
}

/// Decides whether to show LoginScreen or ActivityScreen based on token presence.
///
/// Uses a FutureBuilder so the check is async (token lives in flutter_secure_storage).
/// Shows a loading indicator while the check is in-flight — typically < 100ms.
class _AuthGate extends StatelessWidget {
  const _AuthGate();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: authService.isLoggedIn(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          // Token check in progress — show neutral loading screen
          return const Scaffold(
            backgroundColor: Color(0xFF0A0E1A),
            body: Center(
              child: CircularProgressIndicator(
                color: Color(0xFF6366F1),
                strokeWidth: 2.5,
              ),
            ),
          );
        }

        final isLoggedIn = snapshot.data ?? false;
        if (isLoggedIn) {
          return const ActivityScreen();
        }
        return const LoginScreen();
      },
    );
  }
}
