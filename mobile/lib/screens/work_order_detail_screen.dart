import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';

import '../services/api_client.dart';
import '../services/local_db.dart';

/// Shows a work order and lets the engineer add structured service notes
/// (Initial Condition / Investigation / Outcome / Follow Up). Works offline:
/// notes are queued locally and synced later; see SyncManager.
class WorkOrderDetailScreen extends StatefulWidget {
  final ApiClient api;
  final Map<String, dynamic> workOrder;

  const WorkOrderDetailScreen({super.key, required this.api, required this.workOrder});

  @override
  State<WorkOrderDetailScreen> createState() => _WorkOrderDetailScreenState();
}

class _WorkOrderDetailScreenState extends State<WorkOrderDetailScreen> {
  final _noteController = TextEditingController();
  String _noteType = 'initial_condition';
  bool _saving = false;

  Future<void> _submitNote() async {
    if (_noteController.text.trim().isEmpty) return;
    setState(() => _saving = true);

    final payload = {'note_type': _noteType, 'content': _noteController.text.trim()};
    final connectivity = await Connectivity().checkConnectivity();

    try {
      if (connectivity == ConnectivityResult.none) {
        await LocalDatabase.queueChange(
          entityType: 'service_note',
          entityId: widget.workOrder['id'],
          operation: 'create',
          payload: payload,
        );
        _showSnack('Saved offline - will sync when back online.');
      } else {
        await widget.api.addServiceNote(widget.workOrder['id'], payload);
        _showSnack('Note saved.');
      }
      _noteController.clear();
    } catch (_) {
      // Network call failed even though connectivity looked available
      // (e.g. server unreachable) - fall back to the offline queue rather
      // than losing the engineer's note.
      await LocalDatabase.queueChange(
        entityType: 'service_note',
        entityId: widget.workOrder['id'],
        operation: 'create',
        payload: payload,
      );
      _showSnack('Could not reach server - saved offline instead.');
    } finally {
      setState(() => _saving = false);
    }
  }

  void _showSnack(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    final wo = widget.workOrder;
    return Scaffold(
      appBar: AppBar(title: Text(wo['title'] ?? 'Work Order')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Status: ${wo['status']}', style: const TextStyle(fontWeight: FontWeight.bold)),
            Text('Priority: ${wo['priority']}'),
            const Divider(height: 24),
            const Text('Add Service Note', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DropdownButton<String>(
              value: _noteType,
              items: const [
                DropdownMenuItem(value: 'initial_condition', child: Text('Initial Condition')),
                DropdownMenuItem(value: 'investigation', child: Text('Investigation')),
                DropdownMenuItem(value: 'outcome', child: Text('Outcome')),
                DropdownMenuItem(value: 'follow_up', child: Text('Follow Up')),
                DropdownMenuItem(value: 'general', child: Text('General')),
              ],
              onChanged: (value) => setState(() => _noteType = value ?? 'general'),
            ),
            TextField(
              controller: _noteController,
              maxLines: 4,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Describe what you observed or did...',
              ),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: _saving ? null : _submitNote,
              child: _saving ? const CircularProgressIndicator() : const Text('Save Note'),
            ),
          ],
        ),
      ),
    );
  }
}
