module.exports = {
  lintOnSave: process.env.NODE_ENV !== 'production',
  devServer: {
    client: {
      overlay: {
        warnings: true,
        errors: true
      }
    }
  }
} 