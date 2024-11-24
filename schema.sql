
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE group_roles (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    user_id INTEGER REFERENCES users,
    role TEXT NOT NULL -- meaning defined in RoleEnum.py file
);

CREATE TABLE group_invites (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    invitee_id INTEGER REFERENCES users,
    role TEXT NOT NULL -- meaning defined in RoleEnum.py file
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    archived BOOLEAN NOT NULL DEFAULT FALSE
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TYPE TASK_STATE AS ENUM ('Pending', 'In Progress', 'Completed', 'Archived');
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects,
    title TEXT,
    description TEXT,
    state TASK_STATE DEFAULT 'Pending',
    priority INTEGER DEFAULT 1,
    deadline TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE task_assignments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks,
    user_id INTEGER REFERENCES users,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
