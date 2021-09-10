-- models.pyで実行されるSQL
SELECT
    users.id AS users_id, 
    users.username AS users_username, 
    users.picture_path AS users_picture_path, 
    user_connects_1.status AS joined_status_to_from,
    user_connects_2.status AS joined_status_from_to 
FROM
    users 
    LEFT OUTER JOIN
    user_connects AS user_connects_1 
    ON user_connects_1.from_user_id = users.id 
    AND user_connects_1.to_user_id = ? 
    LEFT OUTER JOIN
    user_connects AS user_connects_2 
    ON user_connects_2.from_user_id = ?
    AND user_connects_2.to_user_id = users.id 
WHERE
    users.username LIKE ? 
    AND users.id != ? 
    AND users.is_active = 1
