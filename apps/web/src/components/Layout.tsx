import { Outlet } from "react-router-dom";
import Header from "./Header";

function Layout(): JSX.Element {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t bg-white py-4 text-center text-sm text-gray-500">
        ITcopilot &copy; {new Date().getFullYear()} — Income Tax Copilot for India
      </footer>
    </div>
  );
}

export default Layout;
