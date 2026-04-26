import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import LoginPage from "@/app/(auth)/login/page";
import { TestProviders } from "@/tests/test-utils";

const pushMock = vi.fn();
const loginMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

vi.mock("@/lib/api", () => ({
  api: {
    login: (...args: unknown[]) => loginMock(...args),
  },
}));

describe("LoginPage", () => {
  it("renders the login form and signs in with demo credentials", async () => {
    loginMock.mockResolvedValue({
      access_token: "token",
      refresh_token: "refresh",
      token_type: "bearer",
        user: {
          id: "USRADMIN",
          company_id: "COM001",
          station_id: null,
          full_name: "Admin User",
          email: "admin@example.com",
          role: "super_admin",
          is_active: true,
        },
    });

    render(
      <TestProviders>
        <LoginPage />
      </TestProviders>,
    );

    expect(screen.getByText("Sign in")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /access dashboard/i }));

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({
        email: "admin@example.com",
        password: "Admin123!",
      });
      expect(pushMock).toHaveBeenCalledWith("/dashboard");
    });
  });
});
