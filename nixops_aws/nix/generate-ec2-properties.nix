
let
  inherit (import <nixpkgs/lib>)
    listToAttrs
    ;
  response = builtins.fromJSON (builtins.readFile ./instance-types.json);

  isSupported = x: {
    "default" = true;
    "supported" = true;
    "required" = true;
    "unsupported" = false;
  }.${x};

  isNVMeSupported = x: {
    "supported" = true;
    "required" = true; # z1d
    "unsupported" = false;
  }.${x};


  summarize = instanceType: {
    cores = instanceType.VCpuInfo.DefaultVCpus;
    memory = instanceType.MemoryInfo.SizeInMiB;
    allowsEbsOptimized = isSupported instanceType.EbsInfo.EbsOptimizedSupport;
    supportsNVMe = isNVMeSupported instanceType.EbsInfo.NvmeSupport;
  };


in listToAttrs (map (v: { name = v.InstanceType; value = summarize v; }) response.InstanceTypes)
