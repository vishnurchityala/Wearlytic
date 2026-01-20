import { useEffect, useState } from "react";
import { getCurrentUserProfile, API_BASE_URL } from "../../api/users";
import { useAuth } from "../../auth/AuthProvider";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFloppyDisk, faUser, faCoins } from "@fortawesome/free-solid-svg-icons";

function ProfileDetailsForm() {
    const { token, user } = useAuth();
    const [form, setForm] = useState({
        name: "",
        info_prompt: "",
        email: "",
        role: "",
        tokens: 0
    });

    const [loading, setLoading] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchProfile() {
            try {
                setError(null);
                if (!token) return;
                const data = await getCurrentUserProfile(token);
                setForm({
                    name: data.name ?? "",
                    info_prompt: data.info_prompt ?? "",
                    email: data.email ?? "",
                    role: data.role ?? "",
                    tokens: data.tokens ?? 0
                });
            } catch (err) {
                setError(err.message || "Failed to load profile");
            } finally {
                setInitialLoading(false);
            }
        }
        fetchProfile();
    }, [token]);

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        if (!user) {
            setLoading(false);
            return;
        }

        await fetch(`${API_BASE_URL}/users/${user.id}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": token ? `Bearer ${token}` : undefined
            },
            body: JSON.stringify({
                name: form.name,
                info_prompt: form.info_prompt
            })
        });

        setLoading(false);
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="bg-white border-2 border-gray-300 rounded-lg shadow-lg p-4 sm:p-6"
        >
            <div className="flex items-center justify-between">
                <h2 className="outfit-regular text-xl sm:text-2xl">Profile Details</h2>
            </div>

            {initialLoading ? (
                <div className="animate-pulse mt-4 space-y-3">
                    <div className="h-9 bg-gray-200 rounded"></div>
                    <div className="h-24 bg-gray-200 rounded"></div>
                    <div className="h-9 bg-gray-200 rounded"></div>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="h-9 bg-gray-200 rounded"></div>
                        <div className="h-9 bg-gray-200 rounded"></div>
                    </div>
                </div>
            ) : error ? (
                <div className="mt-3 text-sm text-red-600">{error}</div>
            ) : (
                <>
                    <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                        <div className="col-span-1">
                            <label className="block text-sm text-gray-700 mb-1">Name</label>
                            <input
                                name="name"
                                value={form.name}
                                onChange={handleChange}
                                placeholder="Your name"
                                className="w-full border-2 border-gray-300 px-3 py-2 rounded-xl bg-white outfit-regular"
                            />
                        </div>
                        <div className="col-span-1">
                            <label className="block text-sm text-gray-700 mb-1">Email</label>
                            <input
                                value={form.email}
                                disabled
                                className="w-full border-2 border-gray-300 px-3 py-2 rounded-xl bg-gray-100 text-gray-600 outfit-regular"
                            />
                        </div>
                    </div>

                    <div className="mt-4">
                        <label className="block text-sm text-gray-700 mb-1">About you</label>
                        <textarea
                            name="info_prompt"
                            value={form.info_prompt}
                            onChange={handleChange}
                            placeholder="Tell us about your style, fit, and preferences…"
                            className="w-full border-2 border-gray-300 px-3 py-2 rounded-xl min-h-28 bg-white outfit-regular"
                        />
                    </div>

                    <div className="mt-4 flex flex-wrap items-center gap-3">
                        <div className="inline-flex items-center px-2.5 py-1 rounded-full border-2 border-gray-300 bg-white text-gray-700 text-xs">
                            <FontAwesomeIcon icon={faUser} className="me-1" />
                            <span className="opacity-80">Role:</span>
                            <span className="ms-1">{form.role || "—"}</span>
                        </div>
                        <div className="inline-flex items-center px-2.5 py-1 rounded-full border-2 border-gray-300 bg-white text-gray-700 text-xs">
                            <FontAwesomeIcon icon={faCoins} className="me-1" />
                            <span className="opacity-80">Tokens:</span>
                            <span className="ms-1">{form.tokens}</span>
                        </div>
                    </div>

                    <div className="mt-5">
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-4 py-1.5 text-sm rounded-full bg-black text-white outfit-regular disabled:opacity-60"
                        >
                            {loading ? "Saving..." : (<><FontAwesomeIcon icon={faFloppyDisk} className="me-2" />Save Changes</>)}
                        </button>
                    </div>
                </>
            )}
        </form>
    );
}

export default ProfileDetailsForm;
