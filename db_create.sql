use lms;
CREATE TABLE `course` (
  `id` smallint NOT NULL,
  `course_name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `student` (
  `id` smallint NOT NULL,
  `student_name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `assignment` (
  `id` smallint NOT NULL,
  `assignment_name` varchar(100) NOT NULL,
  `course_id` smallint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assignment_course_id_idx` (`course_id`),
  CONSTRAINT `assignment_course_id` FOREIGN KEY (`course_id`) REFERENCES `course` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `student_course` (
  `ID` smallint NOT NULL,
  `student_id` smallint NOT NULL,
  `course_id` smallint NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `StudentCourse_course_id_idx` (`course_id`),
  KEY `StudentCourse_student_id_idx` (`student_id`),
  CONSTRAINT `StudentCourse_course_id` FOREIGN KEY (`course_id`) REFERENCES `course` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `StudentCourse_student_id` FOREIGN KEY (`student_id`) REFERENCES `student` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `submission` (
  `id` smallint NOT NULL,
  `course_id` smallint NOT NULL,
  `student_id` smallint NOT NULL,
  `assignment_id` smallint NOT NULL,
  `grade` tinyint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `submission_course_id_idx` (`course_id`),
  KEY `submission_student_id_idx` (`student_id`),
  KEY `submission_assignment_id_idx` (`assignment_id`),
  CONSTRAINT `submission_assignment_id` FOREIGN KEY (`assignment_id`) REFERENCES `assignment` (`id`),
  CONSTRAINT `submission_course_id` FOREIGN KEY (`course_id`) REFERENCES `course` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `submission_student_id` FOREIGN KEY (`student_id`) REFERENCES `student` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
