import 'package:flutter/material.dart';

import 'screens/login_screen.dart';
import 'services/api_client.dart';

/// Phase 1 MVP entry point. The backend base URL below points at a local
/// dev server (`uvicorn app.main:app`, see backend/README or root README);
/// point it at a deployed URL for staging/production builds.
const String kDefaultApiBaseUrl = 'http://localhost:8000';

void main() {
  runApp(const NightBrewFieldOpsApp());
}

class NightBrewFieldOpsApp extends StatelessWidget {
  const NightBrewFieldOpsApp({super.key});

  @override
  Widget build(BuildContext context) {
    final api = ApiClient(baseUrl: kDefaultApiBaseUrl);
    return MaterialApp(
      title: 'NightBrew FieldOps AI',
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: LoginScreen(api: api),
    );
  }
}
