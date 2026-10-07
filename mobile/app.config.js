export default ({ config }) => ({
  ...config,
  version: process.env.APP_VERSION || '0.1.0',
  scheme: 'agronova',
  plugins: ['expo-notifications'],
  extra: {
    apiUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost/api/v1'
  },
  ios: {
    ...config.ios,
    bundleIdentifier: process.env.IOS_BUNDLE_ID || 'com.agronova.app'
  },
  android: {
    ...config.android,
    package: process.env.ANDROID_PACKAGE || 'com.agronova.app'
  }
});
