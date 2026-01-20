import { useState } from "react";
import { API_BASE_URL, getCurrentUserProfile } from "../../api/users";
import { useAuth } from "../../auth/AuthProvider";
import { useEffect, useRef } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUpload } from "@fortawesome/free-solid-svg-icons";

function ProfileImageForm() {
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);
    const { token, user } = useAuth();
    const [preview, setPreview] = useState(null);
		const [previewLoading, setPreviewLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
		const previewUrlRef = useRef(null);

    useEffect(() => {
        async function loadExistingImage() {
            if (!token) return;
            try {
                const data = await getCurrentUserProfile(token);
                if (data?.base_image_path) {
                    setPreview(data.base_image_path);
                }
            } catch {}
        }
        loadExistingImage();
			return () => {
				if (previewUrlRef.current) {
					URL.revokeObjectURL(previewUrlRef.current);
					previewUrlRef.current = null;
				}
			};
    }, [token]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!image || !user) return;

        setLoading(true);
        setError(null);
        setSuccess(false);

        const formData = new FormData();
        formData.append("image", image);

        try {
            const res = await fetch(`${API_BASE_URL}/users/${user.id}/base_image/`, {
                method: "PATCH",
                body: formData,
                headers: {
                    "Authorization": token ? `Bearer ${token}` : undefined,
                    "Accept": "application/json"
                }
            });
            if (!res.ok) {
                const text = await res.text().catch(() => "");
                throw new Error(text || `Upload failed (${res.status})`);
            }
            setSuccess(true);
            try {
                const data = await getCurrentUserProfile(token);
                if (data?.base_image_path) {
                    setPreview(data.base_image_path);
                }
            } catch {}
            setImage(null);
        } catch (err) {
            setError(err.message || "Failed to upload image");
        }

        setLoading(false);
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="bg-white rounded-lg shadow-lg p-4 sm:p-6"
            encType="multipart/form-data"
        >
            <h2 className="outfit-regular text-xl sm:text-2xl mb-3">Profile Image</h2>

            <div className="flex items-center gap-4">
				<div className="relative w-20 h-20 rounded-full bg-gray-100 overflow-hidden flex items-center justify-center">
					{preview ? (
						<>
							<img
								src={preview}
								alt="Preview"
								onLoad={() => setPreviewLoading(false)}
								onError={() => {
									setPreviewLoading(false);
									setError("Failed to load preview");
								}}
								className="w-full h-full object-cover"
							/>
							{previewLoading && (
								<div className="absolute inset-0 bg-white/60 flex items-center justify-center">
									<div className="h-5 w-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
								</div>
							)}
						</>
					) : (
						<span className="text-gray-400 text-sm">No image</span>
					)}
				</div>
                <div className="flex-1">
                    <label className="block text-sm text-gray-700 mb-1">Upload new image</label>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                            const file = e.target.files[0];
                            setImage(file);
                            setSuccess(false);
                            setError(null);
                            if (previewUrlRef.current) {
                                URL.revokeObjectURL(previewUrlRef.current);
                                previewUrlRef.current = null;
                            }
                            if (file) {
                                setPreviewLoading(true);
                                const url = URL.createObjectURL(file);
                                previewUrlRef.current = url;
                                setPreview(url);
                            } else {
                                setPreview(null);
                            }
                        }}
                        className="block w-full text-sm text-gray-700 rounded-xl border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black bg-white outfit-regular"
                    />
                    <p className="text-xs text-gray-500 mt-1">JPG, PNG. Max 5MB.</p>
                </div>
            </div>

            <div className="mt-5">
                <button
                    type="submit"
                    disabled={loading || previewLoading || !image}
                    className="px-4 py-1.5 text-sm rounded-full bg-black text-white outfit-regular disabled:opacity-60"
                >
                    {loading ? "Uploading..." : (<><FontAwesomeIcon icon={faUpload} className="me-2" />Upload</>)}
                </button>
                {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
                {success && <p className="mt-2 text-sm text-green-600">Profile image updated.</p>}
            </div>
        </form>
    );
}

export default ProfileImageForm;
