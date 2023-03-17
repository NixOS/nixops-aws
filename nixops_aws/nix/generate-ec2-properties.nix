
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

  getPlatforms = x: map toPlatform x.ProcessorInfo.SupportedArchitectures;

  # Some machine types are suitable for darwin (and probably only usable with that)
  # This makes the SupperedArchitectures more of a platform list than an architecture
  # list.
  toPlatform = arch: {
    "arm64" = { cpu = "aarch64"; };
    "x86_64" = { cpu = "x86_64"; };

     # wonky but we don't support as old as true i386, which it probably isn't
    "i386" = { cpu = "i686"; };
    "x86_64_mac" = { cpu = "x86_64"; os = "darwin"; };
    "arm64_mac" = { cpu = "aarch64"; os = "darwin"; };
  }.${arch} or (throw "It seems that ec2 has a new CPU architecture: ${arch}");

  summarize = instanceType: {
    cores = instanceType.VCpuInfo.DefaultVCpus;
    memory = instanceType.MemoryInfo.SizeInMiB;
    allowsEbsOptimized = isSupported instanceType.EbsInfo.EbsOptimizedSupport;
    supportsNVMe = isNVMeSupported instanceType.EbsInfo.NvmeSupport;
    platforms = getPlatforms instanceType;
  };


in listToAttrs (map (v: { name = v.InstanceType; value = summarize v; }) response.InstanceTypes)
