import { render, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import { AuthGate } from "@/components/auth-gate";
import { useAuthStore } from "@/store/auth-store";

const replaceMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
}));

describe("AuthGate", () => {
  it("redirects anonymous users to login", async () => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
    });

    render(<AuthGate><div>Secret content</div></AuthGate>);

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith("/login");
    });
  });
});

