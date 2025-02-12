document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed");

    const courseSectionField = document.querySelector('select#id_course_section');
    const topicField = document.querySelector('select#id_topic');

    console.log("Course Section Field:", courseSectionField);
    console.log("Topic Field:", topicField);

    if (courseSectionField && topicField) {
        courseSectionField.addEventListener('change', function () {
            const courseSectionId = this.value;
            console.log("Course Section ID selected:", courseSectionId);

            if (courseSectionId) {
                const fetchUrl = `/admin/course-section-topics/${courseSectionId}/`;
                console.log("Fetching topics from URL:", fetchUrl);

                fetch(fetchUrl)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log("Topics data fetched:", data);
                        topicField.innerHTML = '';

                        data.topics.forEach(topic => {
                            const option = document.createElement('option');
                            option.value = topic.id;
                            option.textContent = topic.title;
                            topicField.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error fetching topics:', error));
            } else {
                topicField.innerHTML = '';
            }
        });
    } else {
        console.error("Course Section or Topic field not found in the DOM.");
    }
});
