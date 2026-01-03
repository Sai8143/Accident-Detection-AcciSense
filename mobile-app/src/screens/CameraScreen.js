import { CameraView, useCameraPermissions } from "expo-camera";
import * as Location from "expo-location";
import { useRef, useState } from "react";
import { View, Text, Button, ActivityIndicator, Alert } from "react-native";
import { sendAlert } from "../services/api";

export default function CameraScreen() {
  const cameraRef = useRef(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [loading, setLoading] = useState(false);

  if (!permission) {
    return (
      <View style={{ flex: 1, justifyContent: "center" }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text>Camera permission required</Text>
        <Button title="Grant Permission" onPress={requestPermission} />
      </View>
    );
  }

  const handleCapture = async () => {
    try {
      setLoading(true);

      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.6,
        skipProcessing: true
      });

      const location = await Location.getCurrentPositionAsync({});

      const response = await sendAlert(
        photo,
        location.coords.latitude,
        location.coords.longitude
      );

      Alert.alert("Detection Result", response.message);

    } catch (error) {
      console.error(error);
      Alert.alert("Error", "Failed to capture or send image");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1 }}>
      <CameraView ref={cameraRef} style={{ flex: 1 }} />
      <Button
        title={loading ? "Processing..." : "Check Accident"}
        onPress={handleCapture}
        disabled={loading}
      />
    </View>
  );
}
