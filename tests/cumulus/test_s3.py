from cumulus_port.aws_client.s3 import s3_join, s3_object_exists


def test_s3_join():
    assert s3_join() == ""

    assert s3_join("foo", "bar") == "foo/bar"
    assert s3_join("foo", "bar/") == "foo/bar/"
    assert s3_join("/foo", "/bar") == "foo/bar"
    assert s3_join("/foo/", "/bar") == "foo/bar"
    assert s3_join("//foo/", "/bar") == "/foo/bar"
    assert s3_join("foo", "bar", "baz", "qux") == "foo/bar/baz/qux"

    assert s3_join(["foo", "bar"]) == "foo/bar"


def test_s3_object_exists(s3_client, s3_bucket):
    obj = s3_bucket.Object("test-key")
    obj.put(Body="test")

    assert s3_object_exists(s3_client, Bucket=obj.bucket_name, Key=obj.key)
    assert not s3_object_exists(s3_client, Bucket=obj.bucket_name, Key="fake")
