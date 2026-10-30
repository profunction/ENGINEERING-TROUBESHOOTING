import 'dart:convert';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

/// Local SQLite cache + offline write queue.
///
/// Design (see OFFLINE_SYNC_DESIGN.md):
/// - `cached_work_orders` / `cached_customers` / `cached_equipment` hold the
///   last-synced snapshot so the app is usable with no network.
/// - `pending_changes` holds writes made while offline (or while a request
///   failed), each tagged with an entity type, id, payload, and the local
///   timestamp. SyncManager drains this queue when connectivity returns.
/// - Conflict rule: before applying a queued update, the server's current
///   `updated_at` for that row is compared against the timestamp the queued
///   change was based on. If the server row is newer, the change is NOT
///   applied silently - it is marked `conflict` for a human to resolve.
class LocalDatabase {
  static Database? _db;

  static Future<Database> instance() async {
    if (_db != null) return _db!;
    final dbPath = join(await getDatabasesPath(), 'nightbrew_fieldops.db');
    _db = await openDatabase(
      dbPath,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE cached_customers (
            id TEXT PRIMARY KEY,
            json TEXT NOT NULL,
            synced_at TEXT NOT NULL
          )
        ''');
        await db.execute('''
          CREATE TABLE cached_work_orders (
            id TEXT PRIMARY KEY,
            json TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            synced_at TEXT NOT NULL
          )
        ''');
        await db.execute('''
          CREATE TABLE cached_equipment (
            id TEXT PRIMARY KEY,
            json TEXT NOT NULL,
            synced_at TEXT NOT NULL
          )
        ''');
        await db.execute('''
          CREATE TABLE pending_changes (
            local_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            payload TEXT NOT NULL,
            base_updated_at TEXT,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
          )
        ''');
      },
    );
    return _db!;
  }

  static Future<void> cacheWorkOrders(List<Map<String, dynamic>> workOrders) async {
    final db = await instance();
    final batch = db.batch();
    final now = DateTime.now().toIso8601String();
    for (final wo in workOrders) {
      batch.insert(
        'cached_work_orders',
        {
          'id': wo['id'],
          'json': jsonEncode(wo),
          'updated_at': wo['updated_at'],
          'synced_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  static Future<List<Map<String, dynamic>>> getCachedWorkOrders() async {
    final db = await instance();
    final rows = await db.query('cached_work_orders', orderBy: 'updated_at DESC');
    return rows.map((r) => jsonDecode(r['json'] as String) as Map<String, dynamic>).toList();
  }

  static Future<void> queueChange({
    required String entityType,
    required String entityId,
    required String operation,
    required Map<String, dynamic> payload,
    String? baseUpdatedAt,
  }) async {
    final db = await instance();
    await db.insert('pending_changes', {
      'entity_type': entityType,
      'entity_id': entityId,
      'operation': operation,
      'payload': jsonEncode(payload),
      'base_updated_at': baseUpdatedAt,
      'created_at': DateTime.now().toIso8601String(),
      'status': 'pending',
    });
  }

  static Future<List<Map<String, dynamic>>> getPendingChanges() async {
    final db = await instance();
    return db.query('pending_changes', where: "status = 'pending'", orderBy: 'created_at ASC');
  }

  static Future<void> markChangeStatus(int localId, String status) async {
    final db = await instance();
    await db.update('pending_changes', {'status': status}, where: 'local_id = ?', whereArgs: [localId]);
  }
}
