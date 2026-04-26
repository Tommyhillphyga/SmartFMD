"use client";

export function triggerDownload(url: string, accessToken: string | null, filename: string) {
  fetch(url, {
    headers: accessToken
      ? {
          Authorization: `Bearer ${accessToken}`,
        }
      : undefined,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error("Export failed");
      }
      const blob = await response.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename;
      anchor.click();
      window.URL.revokeObjectURL(objectUrl);
    })
    .catch((error) => {
      console.error(error);
    });
}

