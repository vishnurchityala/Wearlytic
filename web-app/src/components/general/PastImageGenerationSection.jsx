import { useEffect, useState } from "react";
import { useAuth } from "../../auth/AuthProvider";
import { PastImageGenerations } from "./PastImageGenerations";

function PastImageGenerationSection() {
    const [generations, setGenerations] = useState([]);
    const [loading, setLoading] = useState(true);
    const { token } = useAuth();

    useEffect(() => {
        if (!token) return;

        const fetchGenerations = async () => {
            try {
                const res = await fetch(
                    "https://wearlytic-zbas.onrender.com/api/users/me/generations/",
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }
                );

                if (!res.ok) {
                    throw new Error("Failed to fetch generations");
                }

                const data = await res.json();
                setGenerations(data);
            } catch (err) {
                console.error(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchGenerations();
    }, [token]);

    return (
        <>
            <div className="max-w-5xl mx-5 md:mx-auto">
                <h1 className="outfit-regular text-2xl sm:text-3xl mb-4 sm:mb-6">
                    Generations
                </h1>
            </div>

            <div className="max-w-5xl mx-5 md:mx-auto px-4 sm:px-6 py-6 sm:py-8 bg-white border-2 border-gray-300 rounded-lg mb-5">
                {loading ? (
                    <p className="text-sm text-gray-500">Loading generations...</p>
                ) : (
                    <PastImageGenerations pastImageGenerations={generations} />
                )}
            </div>
        </>
    );
}

export { PastImageGenerationSection };
