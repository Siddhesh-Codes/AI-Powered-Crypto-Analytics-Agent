module.exports = {
  extends: [
    'react-app',
    'react-app/jest'
  ],
  rules: {
    // Add any custom rules here
    '@typescript-eslint/no-unused-vars': 'warn',
    'no-console': 'warn'
  }
};