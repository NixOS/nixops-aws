{ region ? "us-east-1"
, accessKeyId ? "testing"
, ...
}:
{
  network.description = "AWS DLM Testing";
  resources.awsDataLifecycleManager.testDataLifecycleManager =
    {
      inherit region accessKeyId;
      dlmName = "dlm-test";
      description = "some description";
      executionRole = "AWSDataLifecycleManagerDefaultRole";
      resourceTypes = "instance";
      targetTags.foo = "bar";
      excludeBootVolume = true;
      copyTags = true;
      tagsToAdd.bar = "stuff";
    };
}
