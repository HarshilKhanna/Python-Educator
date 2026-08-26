/// auth_service.dart — Secure token storage and auth state management.
///
/// Stores the JWT in flutter_secure_storage (encrypted on-device),
/// NOT shared_preferences (which is unencrypted and inappropriate for credentials).
///
/// Provides:
///   - login / logout
///   - getToken (null if not logged in)
///   - getUserId / getRole from token claims
///   - isTokenExpired for offline queue sync
library;

import 'dart:convert';

import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  static const _tokenKey = 'auth_token';
  static const _userIdKey = 'user_id';
  static const _roleKey = 'user_role';

  // ---------------------------------------------------------------------------
  // Login / Logout
  // ---------------------------------------------------------------------------

  /// Store the JWT and decoded claims after a successful login.
  Future<void> saveToken({
    required String token,
    required String userId,
    required String role,
  }) async {
    await Future.wait([
      _storage.write(key: _tokenKey, value: token),
      _storage.write(key: _userIdKey, value: userId),
      _storage.write(key: _roleKey, value: role),
    ]);
  }

  /// Remove all stored credentials (logout).
  Future<void> clearToken() async {
    await Future.wait([
      _storage.delete(key: _tokenKey),
      _storage.delete(key: _userIdKey),
      _storage.delete(key: _roleKey),
    ]);
  }

  // ---------------------------------------------------------------------------
  // Token retrieval
  // ---------------------------------------------------------------------------

  /// Returns the stored JWT, or null if not logged in.
  Future<String?> getToken() => _storage.read(key: _tokenKey);

  /// Returns the stored user UUID, or null.
  Future<String?> getUserId() => _storage.read(key: _userIdKey);

  /// Returns the stored role ('student' | 'instructor'), or null.
  Future<String?> getRole() => _storage.read(key: _roleKey);

  /// Returns true if there is a non-expired token in storage.
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    if (token == null) return false;
    return !isTokenExpired(token);
  }

  // ---------------------------------------------------------------------------
  // Token inspection (no network needed)
  // ---------------------------------------------------------------------------

  /// Returns true if the JWT's exp claim is in the past.
  ///
  /// Used by the offline queue to decide whether to surface a re-login prompt
  /// rather than attempting (and failing) to sync.
  bool isTokenExpired(String token) {
    try {
      // Decode without verifying signature — we only need the exp claim.
      // Signature verification happens server-side on every API call.
      final jwt = JWT.decode(token);
      final exp = jwt.payload['exp'];
      if (exp == null) return true;
      final expiry = DateTime.fromMillisecondsSinceEpoch(exp * 1000, isUtc: true);
      return DateTime.now().toUtc().isAfter(expiry);
    } catch (_) {
      return true; // malformed token counts as expired
    }
  }
}

/// Singleton instance used throughout the app.
final authService = AuthService();
