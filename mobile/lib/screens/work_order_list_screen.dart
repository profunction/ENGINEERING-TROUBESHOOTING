import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';

import '../services/api_client.dart';
import '../services/local_db.dart';
import '../services/sync_manager.dart';
import 'work_order_detail_screen.dart';

class WorkOrderListScreen extends StatefulWidget {
  final ApiClient api;
  const WorkOrderListScreen({super.key, required this.api});

  @override
  State<WorkOrderListScreen> createState() => _WorkOrderListScreenState();
}

class _WorkOrderListScreenState extends State<WorkOrderListScreen> {
  List<Map<String, dynamic>> _workOrders = [];
  bool _offline = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final connectivity = await Connectivity().checkConnectivity();
    final isOffline = connectivity == ConnectivityResult.none;

    if (!isOffline) {
      try {
        final sync = SyncManager(widget.api);
        await sync.syncPendingChanges();

        final fresh = await widget.api.listWorkOrders();
        final freshList = List<Map<String, dynamic>>.from(fresh);
        await LocalDatabase.cacheWorkOrders(freshList);
        setState(() {
          _workOrders = freshList;
          _offline = false;
        });
      } catch (_) {
        await _loadFromCache();
      }
    } else {
      await _loadFromCache();
    }
    setState(() => _loading = false);
  }

  Future<void> _loadFromCache() async {
    final cached = await LocalDatabase.getCachedWorkOrders();
    setState(() {
      _workOrders = cached;
      _offline = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Work Orders'),
        backgroundColor: _offline ? Colors.orange : null,
      ),
      body: Column(
        children: [
          if (_offline)
            Container(
              width: double.infinity,
              color: Colors.orange.shade100,
              padding: const EdgeInsets.all(8),
              child: const Text(
                'Offline mode - showing cached work orders. AI troubleshooting is unavailable.',
                textAlign: TextAlign.center,
              ),
            ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _load,
                    child: ListView.builder(
                      itemCount: _workOrders.length,
                      itemBuilder: (context, index) {
                        final wo = _workOrders[index];
                        return ListTile(
                          title: Text(wo['title'] ?? ''),
                          subtitle: Text('Status: ${wo['status']} · Priority: ${wo['priority']}'),
                          onTap: () => Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => WorkOrderDetailScreen(api: widget.api, workOrder: wo),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
