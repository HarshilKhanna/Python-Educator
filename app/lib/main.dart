import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'services/auth_service.dart';
import 'providers/settings_provider.dart';

void main() {
  runApp(const ProviderScope(child: PythonEducatorApp()));
}

class PythonEducatorApp extends ConsumerWidget {
  const PythonEducatorApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final scheme = settings.highContrast ? highContrastScheme() : defaultScheme();

    return MaterialApp(
      title: 'Python Educator',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: scheme,
        scaffoldBackgroundColor: settings.highContrast ? Colors.black : const Color(0xFF0A0E1A),
        useMaterial3: true,
        textTheme: const TextTheme().apply(
          fontSizeFactor: 1.0, // base; MediaQuery override below handles scale
          fontFamily: settings.dyslexiaFont ? 'OpenDyslexic' : null,
        ),
      ),
      builder: (context, child) {
        // Apply text scale globally via MediaQuery so it propagates everywhere
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaler: TextScaler.linear(settings.textScale.factor),
            disableAnimations: settings.reducedMotion,
          ),
          child: child!,
        );
      },
      home: const _AuthGate(),
    );
  }
}

/// Decides whether to show LoginScreen or HomeScreen based on token presence.
class _AuthGate extends StatelessWidget {
  const _AuthGate();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: authService.isLoggedIn(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
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
          return const HomeScreen();
        }
        return const LoginScreen();
      },
    );
  }
}
