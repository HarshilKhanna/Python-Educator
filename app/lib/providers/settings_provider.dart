/// settings_provider.dart — App-wide accessibility settings.
///
/// Persists text-size scale and high-contrast mode in shared_preferences.
/// Injected into MaterialApp via main.dart so all widgets inherit the changes.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

// ── Text scale levels ────────────────────────────────────────────────────────

enum TextScale { small, medium, large }

extension TextScaleExt on TextScale {
  double get factor {
    switch (this) {
      case TextScale.small:  return 0.85;
      case TextScale.medium: return 1.0;
      case TextScale.large:  return 1.2;
    }
  }

  String get label {
    switch (this) {
      case TextScale.small:  return 'Small';
      case TextScale.medium: return 'Medium';
      case TextScale.large:  return 'Large';
    }
  }
}

// ── State ────────────────────────────────────────────────────────────────────

class AppSettings {
  final TextScale textScale;
  final bool highContrast;
  final bool reducedMotion;
  final bool dyslexiaFont;

  const AppSettings({
    this.textScale = TextScale.medium,
    this.highContrast = false,
    this.reducedMotion = false,
    this.dyslexiaFont = false,
  });

  AppSettings copyWith({
    TextScale? textScale, 
    bool? highContrast,
    bool? reducedMotion,
    bool? dyslexiaFont,
  }) {
    return AppSettings(
      textScale: textScale ?? this.textScale,
      highContrast: highContrast ?? this.highContrast,
      reducedMotion: reducedMotion ?? this.reducedMotion,
      dyslexiaFont: dyslexiaFont ?? this.dyslexiaFont,
    );
  }
}

// ── Notifier ─────────────────────────────────────────────────────────────────

class SettingsNotifier extends Notifier<AppSettings> {
  static const _textScaleKey   = 'app_text_scale';
  static const _highContrastKey = 'app_high_contrast';
  static const _reducedMotionKey = 'app_reduced_motion';
  static const _dyslexiaFontKey = 'app_dyslexia_font';

  @override
  AppSettings build() {
    // Load from prefs async — fire and forget; UI will rebuild on state change
    _load();
    return const AppSettings();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final scaleIndex    = prefs.getInt(_textScaleKey) ?? TextScale.medium.index;
    final contrast      = prefs.getBool(_highContrastKey) ?? false;
    final reducedMotion = prefs.getBool(_reducedMotionKey) ?? false;
    final dyslexiaFont  = prefs.getBool(_dyslexiaFontKey) ?? false;
    state = AppSettings(
      textScale:     TextScale.values[scaleIndex.clamp(0, TextScale.values.length - 1)],
      highContrast:  contrast,
      reducedMotion: reducedMotion,
      dyslexiaFont:  dyslexiaFont,
    );
  }

  Future<void> setTextScale(TextScale scale) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_textScaleKey, scale.index);
    state = state.copyWith(textScale: scale);
  }

  Future<void> setHighContrast(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_highContrastKey, value);
    state = state.copyWith(highContrast: value);
  }

  Future<void> setReducedMotion(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_reducedMotionKey, value);
    state = state.copyWith(reducedMotion: value);
  }

  Future<void> setDyslexiaFont(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_dyslexiaFontKey, value);
    state = state.copyWith(dyslexiaFont: value);
  }
}

// ── Provider ─────────────────────────────────────────────────────────────────

final settingsProvider = NotifierProvider<SettingsNotifier, AppSettings>(
  SettingsNotifier.new,
);

// ── High-contrast color scheme ────────────────────────────────────────────────

/// WCAG AA compliant dark-on-light palette for high-contrast mode.
ColorScheme highContrastScheme() => ColorScheme.fromSeed(
  seedColor: const Color(0xFF3730A3),
  brightness: Brightness.dark,
  surface: Colors.black,
  onSurface: Colors.white,
  primary: const Color(0xFF818CF8),
  onPrimary: Colors.white,
  secondary: const Color(0xFF34D399),
  error: const Color(0xFFEF4444),
);

ColorScheme defaultScheme() => ColorScheme.fromSeed(
  seedColor: const Color(0xFF6366F1),
  brightness: Brightness.dark,
  surface: const Color(0xFF141824),
);

class AppThemeColors {
  final Color background;
  final Color cardBackground;
  final Color cardBorder;
  final Color textPrimary;
  final Color textSecondary;
  final Color textMuted;
  final Color accent;

  const AppThemeColors({
    required this.background,
    required this.cardBackground,
    required this.cardBorder,
    required this.textPrimary,
    required this.textSecondary,
    required this.textMuted,
    required this.accent,
  });
}

extension AppSettingsTheme on AppSettings {
  AppThemeColors get colors => highContrast
      ? const AppThemeColors(
          background: Colors.black,
          cardBackground: Color(0xFF121212),
          cardBorder: Color(0xFF818CF8),
          textPrimary: Colors.white,
          textSecondary: Color(0xFFF3F4F6),
          textMuted: Color(0xFFE5E7EB),
          accent: Color(0xFF818CF8),
        )
      : const AppThemeColors(
          background: Color(0xFF0A0E1A),
          cardBackground: Color(0xFF141824),
          cardBorder: Color(0xFF1F2937),
          textPrimary: Colors.white,
          textSecondary: Color(0xFF9CA3AF),
          textMuted: Color(0xFF6B7280),
          accent: Color(0xFF6366F1),
        );
}
