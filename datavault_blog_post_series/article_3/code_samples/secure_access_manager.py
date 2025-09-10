#!/usr/bin/env python3
"""
Secure Access Manager for DataVault Financial Services
Implements role-based access control for enterprise compliance
Author: Sarah Rodriguez & David Kim
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import os

class SecureAccessManager:
    """
    Manages role-based access control and audit logging for DataVault's
    global knowledge management system
    """
    
    def __init__(self, db_path: str = "access_control.db"):
        self.db_path = db_path
        self._init_database()
        
        # Permission matrix for different roles
        self.permission_matrix = {
            'executive': {
                'read': ['all'],
                'write': ['global_research', 'client_analytics'],
                'delete': ['none'],
                'export': ['all'],
                'admin': ['view_audit', 'manage_users']
            },
            'analyst': {
                'read': ['global_research', 'internal_training', 'client_analytics'],
                'write': ['global_research'],
                'delete': ['own_content'],
                'export': ['global_research', 'internal_training']
            },
            'compliance_us': {
                'read': ['us_compliance', 'global_research', 'internal_training'],
                'write': ['us_compliance'],
                'delete': ['none'],
                'export': ['us_compliance'],
                'admin': ['view_audit']
            },
            'compliance_eu': {
                'read': ['eu_compliance', 'global_research', 'internal_training'],
                'write': ['eu_compliance'],
                'delete': ['none'],
                'export': ['eu_compliance'],
                'admin': ['view_audit']
            },
            'client_manager': {
                'read': ['client_analytics', 'global_research'],
                'write': ['client_analytics'],
                'delete': ['none'],
                'export': ['client_analytics']
            },
            'employee': {
                'read': ['internal_training'],
                'write': ['none'],
                'delete': ['none'],
                'export': ['none']
            }
        }
    
    def _init_database(self):
        """Initialize SQLite database for audit logging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                user_role TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                allowed BOOLEAN NOT NULL,
                details TEXT
            )
        ''')
        
        # Create user sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                user_role TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def validate_access(self, user_id: str, action: str, resource: str, 
                       user_role: Optional[str] = None) -> Dict:
        """
        Validate if user has permission for specific action on resource
        Returns detailed access decision with audit trail
        """
        
        # Get user profile if role not provided
        if not user_role:
            user_role = self._get_user_role(user_id)
        
        permissions = self.permission_matrix.get(user_role, {})
        allowed_resources = permissions.get(action, [])
        
        # Check permission rules
        is_allowed = False
        reason = ""
        
        # Check for universal access
        if 'all' in allowed_resources:
            is_allowed = True
            reason = f"Role {user_role} has universal {action} access"
        
        # Check for explicit denial
        elif 'none' in allowed_resources:
            is_allowed = False
            reason = f"Role {user_role} is explicitly denied {action} access"
        
        # Check for wildcard patterns (e.g., compliance_*)
        else:
            for allowed in allowed_resources:
                if '*' in allowed:
                    pattern = allowed.replace('*', '')
                    if resource.startswith(pattern):
                        is_allowed = True
                        reason = f"Resource matches pattern {allowed}"
                        break
                elif resource == allowed:
                    is_allowed = True
                    reason = f"Resource explicitly allowed for {user_role}"
                    break
            
            if not is_allowed:
                reason = f"No matching permission for {action} on {resource}"
        
        # Log the access attempt
        self._log_access_attempt(
            user_id=user_id,
            user_role=user_role,
            action=action,
            resource=resource,
            allowed=is_allowed,
            details=reason
        )
        
        return {
            'allowed': is_allowed,
            'user_id': user_id,
            'role': user_role,
            'action': action,
            'resource': resource,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_session(self, user_id: str, user_role: str, 
                      ip_address: Optional[str] = None) -> str:
        """Create a new authenticated session for user"""
        
        session_id = hashlib.sha256(
            f"{user_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_sessions 
            (session_id, user_id, user_role, created_at, expires_at, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            user_id,
            user_role,
            datetime.now().isoformat(),
            (datetime.now() + timedelta(hours=8)).isoformat(),
            ip_address or 'unknown'
        ))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate if session is still active and return user info"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, user_role, expires_at, is_active
            FROM user_sessions
            WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        user_id, user_role, expires_at, is_active = result
        
        # Check if session is expired
        if datetime.fromisoformat(expires_at) < datetime.now():
            self._invalidate_session(session_id)
            return None
        
        if not is_active:
            return None
        
        return {
            'user_id': user_id,
            'role': user_role,
            'session_id': session_id
        }
    
    def _log_access_attempt(self, user_id: str, user_role: str, action: str,
                           resource: str, allowed: bool, details: str):
        """Log access attempt for audit trail"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_log 
            (timestamp, user_id, user_role, action, resource, allowed, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            user_id,
            user_role,
            action,
            resource,
            allowed,
            details
        ))
        
        conn.commit()
        conn.close()
    
    def _invalidate_session(self, session_id: str):
        """Mark session as inactive"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_sessions
            SET is_active = 0
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def _get_user_role(self, user_id: str) -> str:
        """Get user role from database or return default"""
        # In production, this would query the user database
        # For demo, return a default role
        return 'employee'
    
    def get_audit_log(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Retrieve audit log entries with optional filters"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_log"
        params = []
        
        if filters:
            conditions = []
            if 'user_id' in filters:
                conditions.append("user_id = ?")
                params.append(filters['user_id'])
            if 'start_date' in filters:
                conditions.append("timestamp >= ?")
                params.append(filters['start_date'])
            if 'end_date' in filters:
                conditions.append("timestamp <= ?")
                params.append(filters['end_date'])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT 100"
        
        cursor.execute(query, params)
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return results


# Example usage for DataVault compliance team
def main():
    access_manager = SecureAccessManager()
    
    print("DataVault Secure Access Control System")
    print("=" * 50)
    
    # Sarah Rodriguez attempting to access US compliance data
    print("\n1. Sarah Rodriguez - US Compliance Officer")
    print("-" * 40)
    
    # Create session for Sarah
    session_id = access_manager.create_session(
        user_id="srodriguez",
        user_role="compliance_us",
        ip_address="192.168.1.100"
    )
    
    print(f"Session created: {session_id[:16]}...")
    
    # Test various access scenarios
    test_cases = [
        ("read", "us_compliance"),      # Should be allowed
        ("write", "us_compliance"),     # Should be allowed
        ("read", "eu_compliance"),      # Should be denied (wrong region)
        ("export", "us_compliance"),    # Should be allowed
        ("delete", "us_compliance"),    # Should be denied
    ]
    
    for action, resource in test_cases:
        result = access_manager.validate_access(
            user_id="srodriguez",
            action=action,
            resource=resource,
            user_role="compliance_us"
        )
        
        status = "✅ ALLOWED" if result['allowed'] else "❌ DENIED"
        print(f"{status}: {action} on {resource}")
        print(f"  Reason: {result['reason']}")
    
    # Test analyst access
    print("\n2. Lisa Thompson - Senior Analyst")
    print("-" * 40)
    
    lisa_result = access_manager.validate_access(
        user_id="lthompson",
        action="read",
        resource="global_research",
        user_role="analyst"
    )
    
    print(f"Access to global_research: {'✅ ALLOWED' if lisa_result['allowed'] else '❌ DENIED'}")
    
    # Show recent audit log
    print("\n3. Recent Audit Log")
    print("-" * 40)
    
    audit_entries = access_manager.get_audit_log()
    
    for entry in audit_entries[:5]:
        allowed = "✅" if entry['allowed'] else "❌"
        print(f"{allowed} {entry['timestamp'][:19]} - {entry['user_id']} "
              f"({entry['user_role']}) - {entry['action']} on {entry['resource']}")


if __name__ == "__main__":
    main()