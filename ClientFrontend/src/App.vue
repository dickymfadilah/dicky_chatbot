<template>
  <div id="app">
    <!-- <nav class="navbar">
      <div class="container">
        <div class="navbar-brand">
          <h1 class="title">
            LangChain Ollama Chatbot
          </h1>
        </div>
      </div>
    </nav> -->
    <router-view />
  </div>
</template>

<style>
:root {
  --primary-color: #4a6fa5;
  --secondary-color: #166088;
  --accent-color: #4fc08d;
  --background-color: #f5f7fa;
  --text-color: #2c3e50;
  --light-gray: #e9ecef;
  --white: #ffffff;
  --shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-color);
  background-color: var(--background-color);
  line-height: 1.6;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  background-color: var(--white);
  box-shadow: var(--shadow);
  padding: 1rem 0;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.title {
  color: var(--primary-color);
  font-size: 1.5rem;
  font-weight: 600;
}

.navbar-brand {
  display: flex;
  align-items: center;
}
</style> 