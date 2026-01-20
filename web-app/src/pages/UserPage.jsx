import { Navbar } from "../components/general/Navbar";
import ProfileDetailsForm from "../components/general/ProfileDetailsForm";
import ProfileImageForm from "../components/general/ProfileImageForm";

function UserPage() {
    return (
        <div className="min-h-screen">
            <Navbar />

            <section className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
                <h1 className="outfit-regular text-2xl sm:text-3xl mb-4 sm:mb-6">Your Profile</h1>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
                    <div className="md:col-span-1">
                        <ProfileImageForm />
                    </div>
                    <div className="md:col-span-2">
                        <ProfileDetailsForm />
                    </div>
                </div>
            </section>
        </div>
    );
}

export default UserPage;
