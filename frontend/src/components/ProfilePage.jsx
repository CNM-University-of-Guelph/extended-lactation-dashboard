import React, { useState, useEffect } from "react";
import api from "../api";
import "../styles/ProfilePage.css";
import { useNavigate } from 'react-router-dom';

function ProfilePage() {
    const [userInfo, setUserInfo] = useState(null);
    const [passwords, setPasswords] = useState({ old_password: '', new_password: '', confirm_new_password: '' });
    const [newEmail, setNewEmail] = useState('');
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('');
    const [showDeletePopup, setShowDeletePopup] = useState(false);
    const [deleteConfirm, setDeleteConfirm] = useState(false);

    const navigate = useNavigate();

    useEffect(() => {
        fetchUserInfo();
    }, []);

    const fetchUserInfo = async () => {
        try {
            const res = await api.get("/api/profile/info/");
            setUserInfo(res.data);
        } catch (error) {
            console.error("Failed to load user info", error);
        }
    };

    const handlePasswordChange = async () => {
        if (passwords.new_password !== passwords.confirm_new_password) {
            setMessage("New passwords do not match.");
            setMessageType('error');
            return;
        }
    
        try {
            const response = await api.put("/api/profile/change-password/", {
                old_password: passwords.old_password,
                new_password: passwords.new_password,
            });
    
            if (response.status === 200) {
                setMessage("Password updated successfully.");
                setMessageType('success');
                setPasswords({ old_password: '', new_password: '', confirm_new_password: '' });
            }
        } catch (error) {
            if (error.response && error.response.data && error.response.data.new_password) {
                setMessage(`Error: ${error.response.data.new_password[0]}`);
            } else {
                setMessage("Failed to update password.");
            }
            setMessageType('error');
        }
    };

    const handleEmailChange = async () => {
        try {
            await api.put("/api/profile/change-email/", { email: newEmail });
            setMessage("Email updated successfully.");
            setMessageType('success');
        } catch (error) {
            setMessage("Failed to update email.");
            setMessageType('error');
        }
    };

    const handleAccountDeletion = async () => {
        if (deleteConfirm) {
            try {
                await api.delete("/api/profile/delete/", { data: { confirm: true } });
                setMessage("Account deleted successfully.");
                setMessageType('success');
                setShowDeletePopup(false);
                localStorage.clear();
                navigate("/login");
            } catch (error) {
                setMessage("Failed to delete account.");
                setMessageType('error')
            }
        }
    };

    return (
        <div className="profile-page-container">
            <div className="profile-header">
                <h1>Profile</h1>
            </div>
    
            {/* User Info Summary */}
            {userInfo && (
                <div className="user-info-summary">
                    <h2>User Information</h2>
                    <p><strong>Username:</strong> {userInfo.username}</p>
                    <p><strong>Email:</strong> {userInfo.email}</p>
                </div>
            )}
    
            {/* Change Password */}
            <div className="profile-form">
                <h2>Change Password</h2>
                <label>Old Password</label>
                <input 
                    type="password" 
                    placeholder="Old Password" 
                    value={passwords.old_password}
                    onChange={(e) => setPasswords({ ...passwords, old_password: e.target.value })}
                />
                <label>New Password</label>
                <input 
                    type="password" 
                    placeholder="New Password" 
                    value={passwords.new_password}
                    onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })}
                />
                <label>Confirm New Password</label>
                <input 
                    type="password" 
                    placeholder="Confirm New Password" 
                    value={passwords.confirm_new_password}
                    onChange={(e) => setPasswords({ ...passwords, confirm_new_password: e.target.value })}
                />
                <button onClick={handlePasswordChange}>Update Password</button>
            </div>
    
            {/* Change Email */}
            <div className="profile-form">
                <h2>Change Email</h2>
                <label>New Email</label>
                <input 
                    type="email" 
                    placeholder="New Email" 
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                />
                <button onClick={handleEmailChange}>Update Email</button>
            </div>
    
            {/* Delete Account */}
            <div className="profile-form">
                <h2>Delete Account</h2>
                <button onClick={() => setShowDeletePopup(true)}>Delete Account</button>
            </div>

            {/* Popup for Account Deletion Confirmation */}
            {showDeletePopup && (
                <div className="popup-overlay">
                    <div className="popup-container">
                        <h3>Warning</h3>
                        <p>All your data will be permanently deleted. This action cannot be undone.</p>
                        <div className="confirm-delete-section">
                            <input 
                                type="checkbox" 
                                checked={deleteConfirm}
                                onChange={(e) => setDeleteConfirm(e.target.checked)}
                            />
                            <span>I understand the consequences of deleting my account.</span>
                        </div>
                        <button 
                            className="confirm-delete-button" 
                            onClick={handleAccountDeletion} 
                            disabled={!deleteConfirm}
                        >
                            Confirm Account Deletion
                        </button>
                        <button 
                            className="cancel-button" 
                            onClick={() => setShowDeletePopup(false)}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}
    
            {/* Success or Error Message */}
            {message && <p className={messageType === 'error' ? 'error-message' : 'success-message'}>{message}</p>}
        </div>
    );
}

export default ProfilePage;
