**Video Upload Service Requirements**

**1. Storage:**
   - Store videos locally in a specified directory. Ensure the file path is configurable to allow flexibility in storage location.
   - Prepare for future integration with cloud storage solutions such as Amazon S3 for scalability.

**2. API Endpoints:**
   - **Upload Video Endpoint:**
     - Allow users to upload a video file.
     - Perform initial validation on file size, format, and quality.
     - Store the video in the designated local storage path.
     - Split the video into predefined chunks for processing.
     - Publish details of the video chunks to a RabbitMQ queue named "video-processing-pipeline" for further processing.

**3. Video Checks and Validation:**
   - **File Size:** Set a maximum file size limit to prevent system overload. Configure this limit to be adjustable.
   - **File Format:** Accept commonly used video formats (e.g., .mp4, .avi, .mov). Provide a clear error message if the format is not supported.
   - **File Quality:** Assess the resolution and bitrate of the video to ensure it meets minimum quality standards required for processing.

**4. Security and Compliance:**
   - Ensure all uploads are performed over HTTPS to secure data in transit.
   - Implement authentication and authorization to restrict video uploads to authorized users only.
   - Scan uploaded videos for malware as part of the initial processing step.

**5. Performance and Scalability:**
   - Optimize video storage and retrieval processes to handle high volumes of traffic.
   - Consider implementing load balancing and horizontal scaling if the service usage increases.

**6. Error Handling:**
   - Provide meaningful error responses for failed uploads due to network issues, unsupported formats, or file size limitations.
   - Implement retries or alternative routing for messages that fail to publish to the RabbitMQ queue.

**7. Logging and Monitoring:**
    - Make a postgres table to keep track of all vidoe currently being processed and their current status 
   - Log all operations related to video uploads, including success and error states.
   - Monitor the health of the service and the RabbitMQ queue to quickly identify and resolve issues.

** Dev : Yash