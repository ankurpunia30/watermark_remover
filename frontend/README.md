# Peer-to-Peer Learning Platform

An intelligent platform that connects students based on complementary skills and learning needs, enabling collaborative learning and skill development through peer-to-peer interactions.

## Features

- **Matching Algorithm**: Matches students based on complementary skills and learning needs.
- **Virtual Workspaces**: Collaborative spaces for students to work together on projects and learning tasks.
- **Skill Tracking System**: Tracks individual learning progress and skill development.
- **Basic Chat Functionality**: Allows real-time communication between matched peers.
- **Gamification Elements** (Bonus): Includes features such as achievements, badges, and rankings to enhance user engagement.
- **Reputation System** (Bonus): Students can earn reputation based on their contributions to learning and helping others.
- **Skill Recommendations** (Bonus): Personalized suggestions for skills to focus on based on learning progress.
- **Visual Skill Progression** (Bonus): Visual indicators of skill growth and milestones.

## Tech Stack

- **Frontend**: React (Vite), Tailwind CSS
- **Backend**: Node.js, Express
- **Database**: MongoDB
- **Additional Technologies**: WebSockets (for real-time communication), JWT (for authentication)

## Setup and Installation

### Prerequisites

- [Node.js](https://nodejs.org/) (version 14.x or above)
- [MongoDB](https://www.mongodb.com/) (either locally or using MongoDB Atlas)
  
### Frontend

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/peer-to-peer-learning-platform.git
   ```

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open the app in your browser: [http://localhost:3000](http://localhost:3000)

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file and set up the required environment variables (e.g., MongoDB URI, JWT secret).

4. Start the server:
   ```bash
   npm start
   ```

5. The API will be running on [http://localhost:5000](http://localhost:5000).

## Usage

- **Sign up**: Create an account with basic information.
- **Profile**: Fill out your profile with skills you want to learn and skills you can teach.
- **Matching**: The system will match you with peers based on complementary skills.
- **Collaboration**: Use the virtual workspaces to collaborate on tasks and projects.
- **Chat**: Communicate with your matched peers in real-time.

## Contributing

We welcome contributions to improve the platform!

### Steps to Contribute:
1. Fork the repository.
2. Create a new branch for your feature/bug fix.
3. Make your changes.
4. Create a pull request with a description of the changes.

