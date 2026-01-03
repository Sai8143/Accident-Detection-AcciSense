import { API_URL } from "../config";

export async function sendAlert(photo, latitude, longitude) {
  try {
    const formData = new FormData();

    formData.append("image", {
      uri: photo.uri,
      name: "accident.jpg",
      type: "image/jpeg",
    });

    formData.append("latitude", latitude.toString());
    formData.append("longitude", longitude.toString());

    const response = await fetch(`${API_URL}/alert`, {
      method: "POST",
      body: formData, // ❗ NO headers
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text);
    }

    return await response.json();

  } catch (error) {
    console.error("❌ Failed to send alert:", error);
    throw error;
  }
}
