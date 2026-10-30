import 'dart:convert';
import 'package:http/http.dart' as http;

/// Thin REST client for the NightBrew FieldOps AI FastAPI backend.
/// Base URL is configurable so the same build can point at a local dev
/// server, a staging environment, or production.
class ApiClient {
  final String baseUrl;
  String? _token;

  ApiClient({required this.baseUrl});

  void setToken(String? token) {
    _token = token;
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<Map<String, dynamic>> login(String email, String password) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    _throwIfError(resp);
    return jsonDecode(resp.body);
  }

  Future<List<dynamic>> listCustomers() async {
    final resp = await http.get(Uri.parse('$baseUrl/customers'), headers: _headers);
    _throwIfError(resp);
    return jsonDecode(resp.body);
  }

  Future<List<dynamic>> listWorkOrders({String? statusFilter}) async {
    final uri = Uri.parse('$baseUrl/work-orders').replace(
      queryParameters: statusFilter != null ? {'status_filter': statusFilter} : null,
    );
    final resp = await http.get(uri, headers: _headers);
    _throwIfError(resp);
    return jsonDecode(resp.body);
  }

  Future<Map<String, dynamic>> createWorkOrder(Map<String, dynamic> payload) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/work-orders'),
      headers: _headers,
      body: jsonEncode(payload),
    );
    _throwIfError(resp);
    return jsonDecode(resp.body);
  }

  Future<Map<String, dynamic>> updateWorkOrder(String id, Map<String, dynamic> payload) async {
    final resp = await http.patch(
      Uri.parse('$baseUrl/work-orders/$id'),
      headers: _headers,
      body: jsonEncode(payload),
    );
    _throwIfError(resp);
    return jsonDecode(resp.body);
  }

  Future<Map<String, dynamic>> addServiceNote(String workOrderId, Map<String, dynamic> payload) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/work-orders/$workOrderId/notes'),
      headers: _headers,
      body: jsonEncode(payload),
    );
    _throwIfError(resp);
    return jsonDecode(resp.body);
  }

  Future<Map<String, dynamic>> generateReport(String workOrderId, Map<String, dynamic> payload) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/work-orders/$workOrderId/report'),
      headers: _headers,
      body: jsonEncode(payload),
    );
    _throwIfError(resp);
    return jsonDecode(resp.body);
  }

  void _throwIfError(http.Response resp) {
    if (resp.statusCode >= 400) {
      throw ApiException(resp.statusCode, resp.body);
    }
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String body;
  ApiException(this.statusCode, this.body);

  @override
  String toString() => 'ApiException($statusCode): $body';
}
